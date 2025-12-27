# Quick Setup Guide

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The database will be automatically created on first run with sample labs.

### 3. Access the Application

Open your browser and go to: **http://localhost:5000**

### 4. Create Your First Account

1. Click "Register" on the homepage
2. Fill in:
   - Username
   - Email
   - Password (minimum 6 characters)
3. Click "Register"
4. Login with your credentials

### 5. Start Practicing

- Go to "Labs" to see available labs
- Click "Start Lab" on any lab
- Use the terminal interface to configure devices

## Troubleshooting

### Import Errors

If you see import errors, make sure all packages are installed:
```bash
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug python-dotenv
```

### Port Already in Use

If port 5000 is already in use, you can change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080 or any available port
```

### Database Issues

If you need to reset the database:
1. Delete `ccna_labs.db` file
2. Restart the application
3. The database will be recreated automatically

## Next Steps

- Explore the sample labs
- Try different device commands
- Customize labs for your needs
- Add more labs through the Flask shell or by modifying `init_db()` function

