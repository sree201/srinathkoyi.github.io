# How to Rename the Folder

To rename the folder from `portfolio-website` to `CCNA-Website`:

## Windows

### Option 1: Using File Explorer
1. Navigate to the parent directory (e.g., `D:\`)
2. Right-click on the `portfolio-website` folder
3. Select "Rename"
4. Type: `CCNA-Website`
5. Press Enter

### Option 2: Using Command Prompt/PowerShell
```bash
# Navigate to parent directory
cd D:\

# Rename the folder
Rename-Item -Path "portfolio-website" -NewName "CCNA-Website"
```

## After Renaming

After renaming the folder:
1. Update your IDE/editor to open the new folder location
2. If using Git, the repository will automatically track the new location
3. Update any shortcuts or scripts that reference the old folder name
4. If running the application, navigate to the new folder:
   ```bash
   cd D:\CCNA-Website
   python app.py
   ```

## Note

- All internal file references in the code have been updated to use "CCNA-Website"
- The folder name change doesn't affect the application functionality
- Git will track the files regardless of the folder name

