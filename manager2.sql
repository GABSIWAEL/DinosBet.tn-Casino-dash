-- Create the new database
CREATE DATABASE IF NOT EXISTS manager;

-- Use the new database
USE manager;

-- Create the clients table
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
