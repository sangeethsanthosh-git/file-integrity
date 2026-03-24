# File Integrity Verification System

A complete Flask web application for registering trusted file hashes, re-uploading files for integrity checks, and reviewing verification history.

## Features

- User registration and login with secure password hashing
- Session-based access control so users only see their own files
- SHA-256 hashing with 4096-byte chunk reads for large files
- SQLite storage for files and verification history
- Dashboard with total, verified, and modified counts
- Verification history with shortened hash comparisons
- Optional AES-backed hash encryption using `cryptography`

## Project Structure

```text
app.py
schema.sql
requirements.txt
utils/
  hash_utils.py
  encryption.py
templates/
static/
```

## Run Locally

1. Create a Python 3.11 virtual environment:

   ```bash
   py -3.11 -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   venv/Scripts/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Optional: enable encrypted hash storage.

   ```bash
   set ENABLE_HASH_ENCRYPTION=true
   set HASH_ENCRYPTION_KEY=YOUR_FERNET_KEY
   ```

   Generate a key with:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. Start the Flask app:

   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000`.

## Notes

- Uploaded file binaries are not stored permanently; the app stores metadata and hashes only.
- The SQLite database file is created automatically as `file_integrity.db`.
- Hashes are always displayed in shortened form in the UI: first 6 and last 6 characters.
