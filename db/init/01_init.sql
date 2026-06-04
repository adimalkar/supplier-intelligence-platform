-- PostgreSQL initialization script
-- Runs once when the postgres container is first created
-- Creates the Airflow database and enables TimescaleDB

-- Create Airflow metadata database (separate from SIE analytics)
SELECT 'CREATE DATABASE airflow OWNER sie_admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

-- Enable TimescaleDB extension on the analytics database
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
