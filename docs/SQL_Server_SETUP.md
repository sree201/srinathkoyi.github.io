# SQL Server (MSSQL) Setup for CCNA-Website

This document explains how to configure Microsoft SQL Server (Local) to work with this project and provides a sample T-SQL script to create the database and a SQL login.

## Prerequisites
- SQL Server instance installed locally (Developer/Express/Standard)
- SQL Server Management Studio (SSMS) installed (you mentioned SSMS 19)
- ODBC Driver for SQL Server (ODBC Driver 18 or 17) installed on the host
- Python package `pyodbc` installed in the virtualenv

## Steps

1. Start SQL Server and SSMS. Connect using **Server Type**: "Database Engine" and either Windows Authentication or SQL Server Authentication.

2. (Optional but recommended) Enable TCP/IP and confirm SQL Server is listening on port 1433:
   - Open "SQL Server Configuration Manager" -> "SQL Server Network Configuration" -> "Protocols for <INSTANCE>" -> Enable `TCP/IP` and restart the SQL Server service.
   - If you changed the port, note it for the connection string.

---

### SSMS 19 — quick checklist & notes

If you are using **SQL Server Management Studio (SSMS) 19**, follow these SSMS-specific steps and checks before running the setup script:

- Server Type: select **Database Engine** when connecting in SSMS.
- Server name examples:
  - Default instance on local machine: `localhost` or `127.0.0.1`
  - Named instance (Express default): `localhost\SQLEXPRESS`
  - Explicit host and port: `127.0.0.1,1433`
- Authentication:
  - To use the sample login created by the script, choose **SQL Server Authentication** and supply the login/password (see script).
  - If SQL Server Authentication is disabled, enable Mixed Mode authentication:
    1. Right-click your server in Object Explorer → **Properties** → **Security** → select **SQL Server and Windows Authentication mode**.  
    2. Restart the SQL Server service for the change to take effect.
- Create the login via GUI (alternative to running the script):
  - In SSMS Object Explorer → expand the server → right-click **Security** → **New** → **Login...** → choose **SQL Server authentication**, set login name and password, then **User Mapping** → map to `ccna_labs` database and give `db_owner` (or more restricted) role.
- Firewall & port: Ensure Windows Firewall allows inbound on port **1433** (or whichever port TCP/IP uses).
- Test connection from SSMS by connecting with the login (Server Type: Database Engine, Authentication: SQL Server Authentication).

---

3. Create the database and app login (run `sql/sqlserver_setup.sql` in SSMS):

   - Suggested login and DB (change the password immediately):
     - **Login:** `ccna_app`
     - **Password:** `StrongP@ssw0rd!ChangeMe` (example — replace with a strong password of your choice)
     - **Database:** `ccna_labs`

   - To execute the script, open a new query window in SSMS, paste `sql/sqlserver_setup.sql`, and run it.

4. Update `.env` with a SQLAlchemy connection URL for MSSQL:

SQLAlchemy (MSSQL via pyodbc; percent-encode special chars in password):
- Example (if server on same host, default port 1433):

```env
DATABASE_URL=mssql+pyodbc://ccna_app:StrongP%40ssw0rd%21ChangeMe@localhost:1433/ccna_labs?driver=ODBC+Driver+18+for+SQL+Server
```

Note: special characters in the password must be percent-encoded (`@` -> `%40`, `!` -> `%21`).

5. Install Python dependency in your virtual environment:

```bash
pip install pyodbc
```

6. Restart the Flask app. It should now connect to SQL Server and create tables on startup when `init_db()` runs.

## Connection details summary (example)
- Server Type: Database Engine
- Server Name: `localhost` or `localhost\SQLEXPRESS` or `127.0.0.1,1433`
- Authentication: SQL Server Authentication
- Login: `ccna_app`
- Password: `StrongP@ssw0rd!ChangeMe` (replace it)

## Troubleshooting
- If you get a connection refused, ensure the SQL Server service is running and TCP/IP is enabled (see step 2).
- Ensure the Windows firewall allows inbound connections on port 1433 (or your configured port).
- If the ODBC driver is missing, install "ODBC Driver 18 for SQL Server" from Microsoft.

---

If you'd like, I can:
- Generate a secure password and place it in your local `.env` for you, or
- Create the login and database on your behalf if you give me direct access / run the script locally.

Which would you prefer?