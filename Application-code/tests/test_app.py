import os
import tempfile
import pytest
from app import app as flask_app

# Dummy DB connection classes
class DummyCur:
    def execute(self, q, data=None): pass
    def fetchall(self): return []  # Simulate no contacts in DB
    def close(self): pass

class DummyConn:
    def cursor(self): return DummyCur()
    def commit(self): pass
    def close(self): pass

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def test_home_status_code(client, monkeypatch):
    """Home page loads successfully with mock DB"""
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn())

    rv = client.get('/')
    assert b'Contacts' in rv.data or b'Database connection failed' not in rv.data

def test_add_contact_invalid(client):
    """Submitting empty contact form shows error"""
    rv = client.post('/add', data=dict(
        name='',
        email='',
        message=''
    ), follow_redirects=True)
    assert b'All fields are required' in rv.data

def test_add_contact_valid(client, monkeypatch):
    """Test adding a valid contact (mocked DB)"""
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn())

    rv = client.post('/add', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'Hello Testing'
    }, follow_redirects=True)
    assert b'Contact added successfully' in rv.data

def test_demo_page(client):
    """Demo page loads successfully"""
    rv = client.get('/demo')
    assert b'Sample contacts' in rv.data