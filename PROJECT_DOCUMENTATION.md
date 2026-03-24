# File Integrity Verification System

## 1. Project Overview

The **File Integrity Verification System** is a Flask-based web application that allows authenticated users to register file fingerprints, verify files later, and maintain a history of integrity checks.

The system is designed to answer one core question:

**Has this file changed since it was originally registered?**

To answer that, the application:

- accepts a file upload
- generates a SHA-256 hash using chunk-based reading
- stores metadata and the hash in SQLite
- allows the same user to upload a file again for comparison
- records each verification attempt in a history log

This project is suitable for academic demonstrations, portfolio use, small internal tools, or a base implementation for a larger document integrity platform.

---

## 2. Objectives

The project was built to satisfy the following goals:

- provide secure user registration and login
- isolate file records per user
- use SHA-256 instead of MD5
- handle large files efficiently through chunk-based hashing
- record verification history for auditability
- present results through a clean, responsive UI
- optionally support encrypted hash storage

---

## 3. Technology Stack

### Backend

- Python 3.11
- Flask 3.x
- SQLite
- Werkzeug security helpers
- `hashlib` for SHA-256 generation
- `cryptography` for optional encrypted hash storage

### Frontend

- HTML
- CSS
- JavaScript

### Database

- SQLite database file: `file_integrity.db`

---

## 4. Main Features

### 4.1 User Authentication

The application includes:

- user registration
- user login
- user logout
- session-based route protection

Passwords are not stored in plain text. They are hashed using Werkzeug's password hashing utilities before being written to the database.

### 4.2 File Upload and Hash Registration

When a user uploads a file:

- the filename is sanitized with `secure_filename`
- the file is read in chunks of `4096` bytes
- a SHA-256 hash is generated
- metadata is stored in SQLite

Stored file metadata includes:

- `id`
- `user_id`
- `file_name`
- `hash_value`
- `upload_time`

### 4.3 File Verification

To verify a tracked file:

- the user opens the verify page for a specific file
- uploads a comparison file
- the system generates a new SHA-256 hash
- the new hash is compared with the original stored hash

The result is shown using one of these messages:

- `File Verified – No Changes Detected`
- `Warning: File Modified`

### 4.4 Verification History

Every verification attempt is stored in a log table, including:

- original hash used for comparison
- newly generated hash
- result (`match` or `mismatch`)
- timestamp

This allows users to review previous integrity checks in a timeline view.

### 4.5 Dashboard

The dashboard shows:

- total uploaded files
- number of files whose latest verification matched
- number of files whose latest verification detected a mismatch

It also displays the tracked file list with:

- file name
- shortened stored hash
- latest verification status
- latest verification timestamp
- quick links to verify or view history

---

## 5. System Architecture

The application follows a simple modular Flask structure.

### Core Files

- `app.py`
  Main Flask application, route definitions, database access, business logic, and request handling.

- `schema.sql`
  SQLite schema for users, files, and verification logs.

- `utils/hash_utils.py`
  SHA-256 generation and hash shortening helpers.

- `utils/encryption.py`
  Optional encryption and decryption for stored hash values.

- `templates/`
  Jinja2 HTML templates for the UI.

- `static/css/styles.css`
  Responsive styling for the application.

- `static/js/app.js`
  Frontend interactivity for alerts and file input labels.

---

## 6. Project Structure

```text
C:\FIS
|-- app.py
|-- schema.sql
|-- requirements.txt
|-- README.md
|-- PROJECT_DOCUMENTATION.md
|-- file_integrity.db
|-- utils/
|   |-- __init__.py
|   |-- hash_utils.py
|   |-- encryption.py
|-- templates/
|   |-- base.html
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- upload.html
|   |-- verify.html
|   |-- history.html
|-- static/
|   |-- css/
|   |   |-- styles.css
|   |-- js/
|       |-- app.js
|-- uploads/
|-- venv/
```

Note:

- the application currently does **not** permanently store uploaded file binaries
- only metadata and hashes are stored
- the `uploads/` folder exists but is not actively used for persistence in the current implementation

---

## 7. Database Design

The system uses three tables.

### 7.1 Users Table

Purpose:

- stores registered user accounts

Columns:

- `id` - primary key
- `username` - unique username
- `password` - hashed password
- `created_at` - account creation timestamp

### 7.2 Files Table

Purpose:

- stores each file registered by a user

Columns:

- `id` - primary key
- `user_id` - owner of the file
- `file_name` - sanitized file name
- `hash_value` - SHA-256 hash, optionally encrypted
- `upload_time` - timestamp of file registration

### 7.3 Verification Logs Table

Purpose:

- stores each verification attempt

Columns:

- `id` - primary key
- `file_id` - related tracked file
- `old_hash` - original stored hash used at comparison time
- `new_hash` - newly generated hash from uploaded verification file
- `result` - `match` or `mismatch`
- `timestamp` - verification time

### 7.4 Relationships

- one user can own many files
- one file can have many verification logs

### 7.5 Indexes

The schema includes:

- `idx_files_user_id`
- `idx_logs_file_id`

These improve filtering by user and by file history.

---

## 8. Route Documentation

### `/`

Behavior:

- redirects authenticated users to `/dashboard`
- redirects guests to `/login`

### `/register`

Methods:

- `GET`
- `POST`

Purpose:

- create a new user account

Validation:

- username must be 3 to 32 characters
- username supports letters, numbers, `.`, `_`, and `-`
- password must be at least 8 characters
- password and confirm password must match

### `/login`

Methods:

- `GET`
- `POST`

Purpose:

- authenticate an existing user

Behavior:

- checks stored password hash
- starts a session on success
- shows an error flash message on failure

### `/logout`

Methods:

- `GET`

Purpose:

- clear the session and log the user out

### `/dashboard`

Methods:

- `GET`

Purpose:

- display the user's tracked files and summary stats

Protection:

- login required

### `/upload`

Methods:

- `GET`
- `POST`

Purpose:

- register a new file for integrity tracking

Protection:

- login required

### `/verify/<file_id>`

Methods:

- `GET`
- `POST`

Purpose:

- compare a newly uploaded file with a previously stored file hash

Protection:

- login required
- file must belong to the current user

### `/history/<file_id>`

Methods:

- `GET`

Purpose:

- display the full verification history for one tracked file

Protection:

- login required
- file must belong to the current user

---

## 9. Request and Data Flow

### 9.1 Registration Flow

1. User submits registration form.
2. Backend validates username and password.
3. Password is hashed with Werkzeug.
4. User record is inserted into SQLite.
5. User is redirected to login.

### 9.2 Upload Flow

1. Authenticated user selects a file.
2. Backend validates that a file exists and has a safe filename.
3. File stream is hashed using SHA-256 in 4096-byte chunks.
4. The hash is optionally encrypted.
5. File metadata is saved in the `files` table.
6. Dashboard is updated with the new entry.

### 9.3 Verification Flow

1. User opens the verify page for a tracked file.
2. User uploads a comparison file.
3. Backend computes a new SHA-256 hash.
4. Stored hash is decrypted if encryption is enabled.
5. Stored hash and new hash are compared.
6. Result is marked as `match` or `mismatch`.
7. A verification log is inserted into `verification_logs`.
8. UI displays the verification result and shortened old/new hashes.

---

## 10. Hashing Design

The system uses SHA-256 only.

### Why SHA-256

- stronger than MD5
- widely trusted for integrity verification
- readily available in Python's standard library

### Chunk-Based Hashing

Files are read in chunks of `4096` bytes.

Benefits:

- memory efficient
- better for large files
- avoids loading entire files into memory at once

Implemented in:

- `utils/hash_utils.py`

---

## 11. Optional Hash Encryption

The project includes optional encrypted storage for hashes.

### How it works

- if encryption is disabled, hashes are stored as plaintext SHA-256 strings
- if encryption is enabled, hashes are encrypted before writing to the database
- values are decrypted only when comparison or display is needed

### Environment Variables

- `ENABLE_HASH_ENCRYPTION=true`
- `HASH_ENCRYPTION_KEY=<fernet-key>`

### Important Note

The implementation uses the `cryptography` library's Fernet mechanism, which provides AES-backed symmetric encryption with integrity protection.

If encryption is enabled without proper configuration, the application raises a startup error so misconfiguration is caught early.

---

## 12. Security Considerations

### Implemented Security Measures

- secure password hashing with Werkzeug
- session-based route protection
- per-user access control for file records
- secure filename sanitization using `secure_filename`
- SHA-256 instead of MD5
- optional encrypted hash storage
- maximum upload size set to `50 MB`

### Current Security Limitations

- the default `SECRET_KEY` in `app.py` should be replaced in production
- CSRF protection is not currently implemented
- rate limiting is not currently implemented
- account lockout is not currently implemented
- file content type validation is minimal because the app accepts any file type by design

### Recommended Production Improvements

- move `SECRET_KEY` fully to environment variables
- add CSRF protection with Flask-WTF or custom tokens
- add rate limiting
- run behind a production WSGI server
- enable secure cookies over HTTPS
- add audit logging for login events

---

## 13. Validation and Error Handling

The application handles several error scenarios.

### Supported Error Cases

- missing file upload
- invalid file name
- invalid username or password
- duplicate username registration
- file too large
- unauthorized access to protected routes
- attempts to access another user's file

### User Feedback

The frontend uses flash messages for:

- success messages
- error messages
- informational messages

Messages automatically fade out in the UI but can also be dismissed manually.

---

## 14. Frontend Design Summary

The frontend aims to be clean, modern, and responsive.

### UI Characteristics

- responsive layouts for desktop and mobile
- modern card-based design
- dashboard summary cards
- table view for tracked files
- timeline view for verification history
- shortened hash display for readability
- clear status badges for verified and modified results

### JavaScript Features

- auto-dismiss alerts
- manual dismiss buttons for alerts
- dynamic filename preview on file input fields

---

## 15. Duplicate File Handling

The system currently allows multiple records with the same filename for the same user.

This is intentional in the current design because:

- filename alone does not guarantee file identity
- two uploads with the same name may represent different versions
- each upload becomes its own tracked record

If stricter duplicate control is desired, future versions could:

- detect same filename plus same hash
- warn before inserting duplicates
- allow replacement or version grouping

---

## 16. Performance Notes

For the current scope, the application is lightweight and efficient.

Performance characteristics:

- SQLite is sufficient for a single-user or small multi-user environment
- chunked hashing reduces memory usage
- indexes help dashboard and history queries
- no permanent binary file storage keeps disk growth low

For larger deployments, future upgrades could include:

- PostgreSQL or MySQL
- background workers for very large file processing
- pagination for long histories
- object storage integration if binary retention is required

---

## 17. Setup and Run Instructions

### Environment Setup

```bash
py -3.11 -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Optional Encryption Setup

```bash
set ENABLE_HASH_ENCRYPTION=true
set HASH_ENCRYPTION_KEY=YOUR_FERNET_KEY
python app.py
```

To generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 18. Files Included in the Delivered Project

### Backend

- `app.py`
- `schema.sql`
- `utils/hash_utils.py`
- `utils/encryption.py`

### Templates

- `templates/base.html`
- `templates/login.html`
- `templates/register.html`
- `templates/dashboard.html`
- `templates/upload.html`
- `templates/verify.html`
- `templates/history.html`

### Static Assets

- `static/css/styles.css`
- `static/js/app.js`

### Documentation

- `README.md`
- `PROJECT_DOCUMENTATION.md`

---

## 19. Testing and Verification Performed

The project has been validated with:

- Python syntax compilation
- dependency installation into the local Python 3.11 virtual environment
- Flask test-client smoke testing

Verified flows:

- user registration
- user login
- file upload
- successful verification match
- mismatch detection
- verification history retrieval

---

## 20. Current Limitations

The current version is functional and complete for the requested scope, but a few limitations remain:

- no password reset flow
- no admin panel
- no email verification
- no file deletion UI
- no profile management
- no pagination on dashboard/history pages
- no permanent storage of original uploaded files
- no CSRF token protection yet

---

## 21. Suggested Future Enhancements

- add file deletion and archive actions
- add search and filtering on the dashboard
- group versions of the same file
- export verification reports as PDF or CSV
- add API endpoints for integration with other systems
- add email alerts when a mismatch is detected
- add role-based access control
- add digital signature support
- add multi-factor authentication

---

## 22. Conclusion

This project successfully implements a complete **File Integrity Verification System** using Flask, SQLite, HTML, CSS, and JavaScript.

It meets the requested requirements by delivering:

- secure authentication
- SHA-256-based file integrity tracking
- per-user file ownership
- verification with clear result messaging
- verification history logging
- responsive UI
- optional encrypted hash storage

The codebase is clean, modular, and ready to run locally with Python 3.11.
