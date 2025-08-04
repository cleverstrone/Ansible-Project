from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", ""),  # ✅ FIXED: Changed from "assd" to "localhost"
            dbname=os.getenv("DB_NAME", ""),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            port=os.getenv("DB_PORT", 5432)
        )
        return conn
    except psycopg2.Error as e:
        flash(f"Database connection error: {e}", "error")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        return render_template('index.html', contacts=[], error="Database connection failed")

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts ORDER BY id ASC")
        contacts = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', contacts=contacts)
    except psycopg2.Error as e:
        flash(f"Database error: {e}", "error")
        return render_template('index.html', contacts=[])

@app.route('/add', methods=['POST'])
def add_contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    # ✅ ENHANCED: Better validation
    if not all([name, email, message]):
        flash("All fields are required!", "error")
        return redirect(url_for('index'))

    if len(name) < 2:
        flash("Name must be at least 2 characters long!", "error")
        return redirect(url_for('index'))

    if '@' not in email or '.' not in email:
        flash("Please enter a valid email address!", "error")
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                   (name, email, message))
        conn.commit()
        cur.close()
        conn.close()
        flash("Contact added successfully!", "success")
    except psycopg2.Error as e:
        flash(f"Error adding contact: {e}", "error")

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')  # ✅ FIXED: Added <int:id> parameter
def delete_contact(id):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        # Check if contact exists first
        cur.execute("SELECT name FROM contacts WHERE id = %s", (id,))
        contact = cur.fetchone()

        if not contact:
            flash("Contact not found!", "error")
            return redirect(url_for('index'))

        cur.execute("DELETE FROM contacts WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash(f"Contact '{contact[0]}' deleted successfully!", "success")
    except psycopg2.Error as e:
        flash(f"Error deleting contact: {e}", "error")

    return redirect(url_for('index'))

@app.route('/edit/<int:id>')  # ✅ FIXED: Added <int:id> parameter
def edit_contact(id):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE id = %s", (id,))
        contact = cur.fetchone()
        cur.close()
        conn.close()

        if not contact:
            flash("Contact not found!", "error")
            return redirect(url_for('index'))

        return render_template('edit.html', contact=contact)
    except psycopg2.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])  # ✅ FIXED: Added <int:id> parameter and POST method
def update_contact(id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    # ✅ ENHANCED: Better validation
    if not all([name, email, message]):
        flash("All fields are required!", "error")
        return redirect(url_for('edit_contact', id=id))

    if len(name) < 2:
        flash("Name must be at least 2 characters long!", "error")
        return redirect(url_for('edit_contact', id=id))

    if '@' not in email or '.' not in email:
        flash("Please enter a valid email address!", "error")
        return redirect(url_for('edit_contact', id=id))

    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        # Check if contact exists first
        cur.execute("SELECT name FROM contacts WHERE id = %s", (id,))
        old_contact = cur.fetchone()

        if not old_contact:
            flash("Contact not found!", "error")
            return redirect(url_for('index'))

        cur.execute("UPDATE contacts SET name=%s, email=%s, message=%s WHERE id=%s",
                   (name, email, message, id))
        conn.commit()
        cur.close()
        conn.close()
        flash(f"Contact '{name}' updated successfully!", "success")
    except psycopg2.Error as e:
        flash(f"Error updating contact: {e}", "error")

    return redirect(url_for('index'))

# ✅ NEW: Demo/Sample page as requested
@app.route('/demo')
def demo_page():
    # Sample data for demonstration
    sample_contacts = [
        (1, "John Doe", "john.doe@example.com", "Hello! I'm John, a software developer interested in your services.", datetime.now()),
        (2, "Jane Smith", "jane.smith@company.com", "Hi there! I'd like to discuss a potential collaboration.", datetime.now()),
        (3, "Mike Johnson", "mike.j@email.com", "Great website! Looking forward to working together.", datetime.now()),
        (4, "Sarah Wilson", "sarah.wilson@corp.com", "I have some questions about your products and services.", datetime.now()),
        (5, "David Brown", "david.brown@startup.io", "Impressive work! Let's connect and explore opportunities.", datetime.now())
    ]
    return render_template('demo.html', contacts=sample_contacts)

# ✅ NEW: API endpoint to populate sample data
@app.route('/populate-sample')
def populate_sample_data():
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed!", "error")
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()

        # Clear existing data
        cur.execute("DELETE FROM contacts")

        # Insert sample data
        sample_data = [
            ("John Doe", "john.doe@example.com", "Hello! I'm John, a software developer interested in your services."),
            ("Jane Smith", "jane.smith@company.com", "Hi there! I'd like to discuss a potential collaboration."),
            ("Mike Johnson", "mike.j@email.com", "Great website! Looking forward to working together."),
            ("Sarah Wilson", "sarah.wilson@corp.com", "I have some questions about your products and services."),
            ("David Brown", "david.brown@startup.io", "Impressive work! Let's connect and explore opportunities.")
        ]

        for name, email, message in sample_data:
            cur.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                       (name, email, message))

        conn.commit()
        cur.close()
        conn.close()
        flash("Sample data added successfully! You can now test all operations.", "success")
    except psycopg2.Error as e:
        flash(f"Error adding sample data: {e}", "error")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
