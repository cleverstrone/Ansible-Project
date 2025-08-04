-- Create database only if it does not exist
DO $$
BEGIN
    PERFORM 1 FROM pg_database WHERE datname = 'contactdb';
    IF NOT FOUND THEN
        EXECUTE 'CREATE DATABASE contactdb';
    END IF;
EXCEPTION WHEN others THEN
    RAISE NOTICE 'Could not create database or already exists.';
END
$$;

-- Safely drop the table if it exists
DROP TABLE IF EXISTS contacts;

-- Create the contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL CHECK (length(name) >= 2),
    email VARCHAR(100) NOT NULL CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    message TEXT NOT NULL CHECK (length(message) <= 1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
