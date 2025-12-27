-- SQL Server setup script for CCNA-Website
-- Run this in SSMS with an administrative account (e.g., sa or a sysadmin account)

-- 1) Create the database
CREATE DATABASE ccna_labs;
GO

USE ccna_labs;
GO

-- 2) Create a login for the app (replace the password with a strong one)
-- Note: change 'StrongP@ssw0rd!ChangeMe' to a secure password before running
CREATE LOGIN ccna_app WITH PASSWORD = 'Qwerty@8978!', CHECK_POLICY = ON;
GO

-- 3) Create a database user mapped to the login
CREATE USER ccna_app FOR LOGIN ccna_app;
GO

-- 4) Grant ownership (or more restricted permissions if you prefer)
ALTER ROLE db_owner ADD MEMBER ccna_app;
GO

-- End of script
