-- Create the database
CREATE DATABASE IF NOT EXISTS manager;

-- Use the database
USE manager;

-- Create the clients table
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create the operations table
CREATE TABLE IF NOT EXISTS operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(255) NOT NULL,
    operation VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    number VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL
);
