# File Integrity Verification System

Academic Project Documentation

---

## Contents

1. [Title Page](#1-title-page)
2. [Abstract](#2-abstract)
3. [Introduction](#3-introduction)
4. [Problem Statement](#4-problem-statement)
5. [Objectives](#5-objectives)
6. [Scope](#6-scope)
7. [Literature Survey](#7-literature-survey)
8. [Existing System](#8-existing-system)
9. [Proposed System](#9-proposed-system)
10. [System Architecture](#10-system-architecture)
11. [Module Description](#11-module-description)
12. [Database Design](#12-database-design)
13. [Algorithm: SHA-256 Hashing](#13-algorithm-sha-256-hashing)
14. [Technology Stack](#14-technology-stack)
15. [UI Design](#15-ui-design)
16. [Implementation Details](#16-implementation-details)
17. [Testing](#17-testing)
18. [Results](#18-results)
19. [Deployment](#19-deployment)
20. [Security Features](#20-security-features)
21. [Advantages](#21-advantages)
22. [Limitations](#22-limitations)
23. [Future Enhancements](#23-future-enhancements)
24. [Conclusion](#24-conclusion)
25. [References](#25-references)

---

## 1. Title Page

**Project Title:** File Integrity Verification System

**Document Type:** Detailed Academic Project Documentation

**Domain:** Cybersecurity / Web Application Development / Digital Integrity Verification

**Technology Base:** Python 3.11, Flask 3.1, SQLite, HTML, CSS, JavaScript

**Prepared By:** Sangeeth Santhosh SA

**Repository Context:** Flask application for authenticated file fingerprint registration, comparison-based integrity verification, verification logging, and optional encrypted hash storage

**Prepared On:** March 24, 2026

**Intended Use:** Project report, viva support document, academic submission, and PDF conversion

---

## 2. Abstract

Digital files are central to modern communication, administration, legal exchange, education, software delivery, and business operations. As dependence on digital documents grows, the risk of accidental modification, unauthorized editing, corruption during transfer, or deliberate tampering also increases. In many small organizations and academic settings, users still depend on manual naming conventions, timestamps, or informal assumptions to decide whether a file has changed. These methods are unreliable because a file can preserve its name while its content changes completely. This creates a practical need for systems that can verify content integrity in a simple, repeatable, and user-friendly manner.

The File Integrity Verification System addresses this need through a lightweight web-based solution built with Flask. The application allows a registered user to upload a file, generate a SHA-256 cryptographic fingerprint for that file, and store the fingerprint along with metadata in a SQLite database. At a later time, the same user can upload another file for comparison. The system computes a new SHA-256 hash for the uploaded comparison file and checks whether it matches the stored trusted hash. If the values are identical, the system concludes that no content change has occurred. If the values differ, the system reports that the file has been modified.

In addition to core comparison logic, the project includes session-based authentication, per-user file isolation, verification logging, optional encrypted storage of hash values, flash-message based user feedback, and a responsive user interface suitable for desktop and mobile devices. The implementation avoids permanent storage of file binaries and instead focuses on storing metadata and cryptographic results, which keeps the design lightweight and reduces storage overhead. The application is also structured for deployment on Render using `gunicorn`, making it suitable for academic demos and small production scenarios.

This document presents a full academic analysis of the project, including the problem background, objectives, system design, database model, SHA-256 hashing algorithm, module-level implementation, testing strategy, deployment workflow, security features, limitations, and future enhancements. The report is based directly on the current codebase and reflects the actual architecture and behavior of the implemented system.

---

## 3. Introduction

### 3.1 Background

Information integrity is one of the foundational goals of information security. While confidentiality protects information from unauthorized disclosure and availability ensures continued access, integrity ensures that information remains correct, complete, and unaltered except through authorized actions. In practice, integrity verification is crucial in domains such as document management, evidence handling, software release validation, legal records, research datasets, financial statements, and configuration management.

File integrity verification generally relies on cryptographic hashing. A cryptographic hash function takes arbitrary input data and produces a fixed-length output called a digest or fingerprint. A strong hash function ensures that even a tiny change in the input data produces a significantly different output. As a result, comparing the stored hash of a trusted file with the freshly computed hash of a new file is an effective way to determine whether the underlying content remains unchanged.

### 3.2 Motivation

Many available integrity tools are either:

- command-line oriented and therefore inconvenient for non-technical users,
- designed for full system monitoring rather than simple per-file verification,
- dependent on infrastructure that is too heavy for a small academic project, or
- lacking user-level authentication and audit-oriented logging.

This project was motivated by the need to build a simple, understandable, and secure web application that demonstrates how cryptographic hashing can be applied to real-world file verification. The system is intentionally compact, but it incorporates meaningful software engineering practices such as modular helper functions, database normalization, validation, access control, responsive design, and environment-based configuration.

### 3.3 Purpose of the Project

The purpose of the File Integrity Verification System is to provide a practical platform that:

- registers trusted file fingerprints,
- verifies later uploads against those fingerprints,
- isolates each user's data,
- logs verification activity, and
- presents results through a clean browser-based interface.

### 3.4 Relevance

The project is academically relevant because it brings together concepts from cybersecurity, web development, database design, applied cryptography, and secure software engineering. It is also practically relevant because it addresses a genuine operational problem with a design small enough to understand and extend.

---

## 4. Problem Statement

Organizations and individuals often exchange digital files whose integrity must be trusted. Examples include signed forms, source archives, policy documents, certificates, research submissions, image evidence, and configuration files. In many situations, users lack a simple method to determine whether a later version of a file is identical to the original trusted version. They may rely on filenames, visible content, or modification timestamps, none of which provide cryptographic assurance.

The problem can be stated as follows:

> There is a need for a secure, lightweight, and user-friendly system that can register a trusted file state, later compare another file against that state using a robust cryptographic method, and clearly report whether the content has changed.

The problem becomes more important when the solution must also:

- support authenticated access,
- ensure one user's data is not visible to another,
- retain a verification trail for audit purposes,
- avoid storing sensitive file contents unnecessarily,
- remain deployable with low infrastructure overhead, and
- remain usable on both desktop and mobile devices.

The existing codebase addresses this problem through comparison-driven verification using SHA-256 hashes stored in a SQLite-backed Flask application.

---

## 5. Objectives

### 5.1 Primary Objective

To design and implement a web-based file integrity verification system that allows authenticated users to register trusted file fingerprints and later verify whether a comparison file has remained unchanged.

### 5.2 Specific Objectives

1. To implement secure user registration and login functionality.
2. To generate SHA-256 hashes for uploaded files using memory-efficient chunk-based reading.
3. To store trusted file metadata and associated hashes in a relational database.
4. To compare a newly uploaded file against a previously stored hash and report a match or mismatch.
5. To record each verification event in a separate verification log.
6. To support optional encrypted storage of hash values using environment-driven configuration.
7. To provide a responsive and easy-to-understand user interface.
8. To prepare the project for local execution and lightweight cloud deployment.

### 5.3 Non-Functional Objectives

- Maintain code readability and modularity.
- Ensure low resource consumption for a student-scale deployment.
- Avoid unnecessary binary storage.
- Keep the workflow simple enough for non-technical users.
- Preserve security best practices where feasible within project scope.

---

## 6. Scope

### 6.1 Functional Scope

The implemented project supports the following functions:

- user registration,
- user login and logout,
- upload of a file for trusted hash registration,
- storage of file metadata and a SHA-256 fingerprint,
- later comparison of another uploaded file with the stored trusted hash,
- display of a match or mismatch result,
- logging of verification attempts,
- viewing of verification history through a dedicated history route,
- optional encryption of hash values,
- responsive layout for multiple device sizes.

### 6.2 Technical Scope

The project uses:

- Flask as the web framework,
- Jinja2 templates for rendering,
- SQLite as the database,
- Werkzeug helpers for password hashing and filename sanitization,
- Python's `hashlib` for SHA-256 generation,
- the `cryptography` package for optional Fernet encryption,
- `gunicorn` for deployment on Render.

### 6.3 User Scope

The system is designed for:

- students,
- small teams,
- instructors evaluating applied security projects,
- users who need a simple web interface for comparing file integrity.

### 6.4 Out-of-Scope Items

The current implementation does not include:

- multi-factor authentication,
- password reset,
- e-mail verification,
- role-based administration,
- distributed storage,
- object storage integration,
- API endpoints for third-party automation,
- full test-suite automation with `pytest`,
- permanent storage of original uploaded file contents.

---

## 7. Literature Survey

### 7.1 Integrity Verification as a Security Requirement

The concept of integrity is well established in information security theory. Integrity-focused systems are designed to ensure that stored or transmitted data is not altered without detection. In practice, this is often achieved through cryptographic digests, message authentication codes, digital signatures, or full file monitoring systems. For many academic and small operational settings, cryptographic file hashing provides an excellent balance between simplicity and reliability.

### 7.2 Cryptographic Hash Functions in Practice

The literature on secure hashing identifies properties such as determinism, preimage resistance, second-preimage resistance, and collision resistance as essential for integrity use cases [1], [2]. Older algorithms such as MD5 and SHA-1 have known weaknesses and are no longer recommended for security-sensitive integrity checks. SHA-256, a member of the SHA-2 family, remains widely accepted for practical verification workflows due to its strong security posture and broad implementation support.

### 7.3 Hashing for File-Level Integrity

File-level integrity verification systems typically store a trusted digest for a known file state and later recompute the digest for comparison. This technique is efficient because the application does not need to interpret the file's content or understand its internal format. A document, image, executable, archive, or text file can all be processed uniformly as binary data. This generality makes cryptographic hashing particularly suitable for browser-based file comparison tools.

### 7.4 Authentication and Access Control in Web Security

Academic and industry guidance on secure web systems emphasizes the importance of authenticated access, session management, password hashing, input validation, and authorization checks [3], [4], [8]. A verification tool that lacks per-user isolation could leak file metadata or allow one user to inspect another user's tracked files. Therefore, even in a compact project, authentication and route protection are critical architectural requirements.

### 7.5 Lightweight Persistence for Small Systems

SQLite is widely recognized as a suitable relational database for embedded, low-to-medium scale applications, prototypes, and academic systems [5]. It offers structured storage, relational modeling, and SQL query capability without requiring a separate database server. For a project that stores users, file metadata, and verification logs, SQLite provides sufficient capability with minimal operational overhead.

### 7.6 Optional Encryption of Stored Sensitive Values

Although hashes are not the same as the original file contents, they may still be treated as sensitive operational data in some environments. The use of symmetric encryption for stored values can help protect data at rest. The `cryptography` library's Fernet mechanism provides authenticated symmetric encryption with key-based access control [6]. In this project, encryption remains optional so that the system can stay easy to deploy while still demonstrating stronger storage protection when required.

### 7.7 Gap Identified in Survey

The survey indicates a gap between heavyweight enterprise monitoring tools and simple, user-oriented educational systems. Many solutions either:

- assume command-line proficiency,
- monitor entire systems rather than user-selected files,
- do not provide individual user accounts,
- lack clean web interfaces, or
- are too complex for teaching and demonstration.

The present project fills this gap by offering a focused web application for comparison-based integrity verification with secure login, audit logging, and optional encrypted hash storage.

---

## 8. Existing System

Before proposing the current solution, it is useful to understand how similar tasks are often handled in traditional or informal environments.

### 8.1 Common Existing Approaches

1. Manual comparison based on filename or timestamp
2. Local command-line checksum tools
3. Basic file monitoring scripts without authentication
4. Spreadsheet or paper-based audit tracking
5. Legacy checksum workflows based on weaker algorithms

### 8.2 Drawbacks of Existing Approaches

#### 8.2.1 Filename and Timestamp Dependence

These attributes do not guarantee content integrity. A file may retain the same name and still be modified internally.

#### 8.2.2 Technical Accessibility Issues

Command-line checksum tools can be effective, but they are not intuitive for many end users and provide little workflow structure.

#### 8.2.3 Lack of Multi-User Isolation

Informal systems usually do not maintain per-user ownership, which can create privacy and authorization issues.

#### 8.2.4 Poor Auditability

Many manual methods do not provide structured verification records that can later be reviewed.

#### 8.2.5 Weak Algorithm Usage

Some older systems still rely on MD5 or SHA-1, both of which are no longer ideal for modern integrity assurance.

### 8.3 Need for Improvement

The limitations above justify the creation of a web-based solution that combines usability, stronger hashing, user authentication, logging, and deployment simplicity.

---

## 9. Proposed System

The proposed system is a Flask-based web application that allows a user to create an account, upload a file to register its trusted fingerprint, and later compare another file against that stored value. The application is intentionally designed around a simple question:

> Does the newly uploaded file produce the same SHA-256 hash as the previously trusted file?

### 9.1 Core Workflow

1. A user registers and logs in.
2. The user uploads a file for tracking.
3. The application calculates a SHA-256 digest.
4. The digest and metadata are stored in SQLite.
5. Later, the user opens the verification page for that tracked file.
6. The user uploads a comparison file.
7. The application calculates a new SHA-256 digest.
8. The new digest is compared with the stored trusted digest.
9. The result is shown as either:
   - `File Verified - No Changes Detected`, or
   - `Warning: File Modified`
10. The verification event is logged for historical reference.

### 9.2 Design Philosophy

The proposed system emphasizes:

- simplicity of use,
- correctness of cryptographic comparison,
- minimal storage overhead,
- secure account isolation,
- maintainability of code,
- responsiveness of user interface,
- optional stronger protection through encrypted hash storage.

### 9.3 Current Client-Facing Behavior

In the present project state, the verification page is optimized for a direct compare-and-result workflow. Recent verification history is still queried and backend logging remains active, but the history panel inside the verify page is temporarily hidden for client-facing delivery. A dedicated history route and template continue to exist in the system.

---

## 10. System Architecture

### 10.1 Architectural Style

The project follows a layered Flask application structure with clear separation between presentation, route handling, helper utilities, and persistence.

### 10.2 High-Level Architecture

```text
+----------------------+
|   Client Browser     |
| HTML / CSS / JS UI   |
+----------+-----------+
           |
           v
+----------------------+
|   Flask Web Layer    |
| Routes + Templates   |
+----------+-----------+
           |
           v
+----------------------+
| Application Logic    |
| Auth / Validation    |
| Hashing / Logging    |
+----------+-----------+
           |
     +-----+------+
     |            |
     v            v
+---------+   +------------------+
| SQLite  |   | Utility Modules  |
| Database|   | Hash + Encryption|
+---------+   +------------------+
```

### 10.3 Layer Description

#### Presentation Layer

This layer consists of Jinja2 templates, shared CSS, and a small amount of JavaScript for alert dismissal and file input display. It presents forms, tables, status banners, and responsive layouts.

#### Web/Application Layer

This layer is implemented in `app.py`. It defines routes, loads the logged-in user, performs input validation, handles sessions, coordinates database operations, and returns rendered templates or redirects.

#### Utility Layer

This layer contains reusable helper logic:

- `utils/hash_utils.py` for SHA-256 hashing and shortened display values
- `utils/encryption.py` for optional hash encryption and decryption

#### Data Layer

The data layer uses SQLite with three normalized tables: `users`, `files`, and `verification_logs`.

### 10.4 Request Flow

#### Registration Flow

Browser -> `/register` -> input validation -> password hashing -> database insert -> redirect to login

#### Upload Flow

Browser -> `/upload` -> file validation -> SHA-256 generation -> optional encryption -> database insert -> redirect to dashboard

#### Verification Flow

Browser -> `/verify/<file_id>` -> ownership check -> stored hash retrieval -> comparison file hash generation -> match/mismatch calculation -> verification log insert -> result display

### 10.5 Architectural Strengths

- easy to understand for academic presentation,
- low operational overhead,
- clear route-to-template mapping,
- reusable helper functions,
- suitable for incremental enhancement.

---

## 11. Module Description

### 11.1 Main Application Module: `app.py`

This file is the operational core of the system. It contains:

- Flask application initialization,
- configuration loading,
- database connection management,
- session handling,
- route definitions,
- helper routines for file access and status reporting,
- error handling.

Important responsibilities include:

- setting `SECRET_KEY`,
- setting `MAX_CONTENT_LENGTH` to 50 MB,
- setting `HASH_CHUNK_SIZE` to 4096 bytes,
- enabling `SESSION_COOKIE_HTTPONLY`,
- enabling `SESSION_COOKIE_SAMESITE="Lax"`,
- validating encryption configuration at startup.

### 11.2 Authentication Module

Authentication is implemented through the following routes and helpers:

- `/register`
- `/login`
- `/logout`
- `load_logged_in_user()`
- `login_required`

Password storage is handled using `generate_password_hash()` and `check_password_hash()` from Werkzeug. Session state is maintained through Flask's session system using `user_id`.

### 11.3 Database Access Module

The functions `get_db()`, `init_db()`, and `close_db()` manage the SQLite lifecycle. The connection uses `sqlite3.Row` so template and route logic can access columns by name.

### 11.4 File Registration Module

The upload workflow is handled by `/upload`. It validates the uploaded file, computes the SHA-256 hash, optionally encrypts the hash, stores metadata, and redirects back to the dashboard.

### 11.5 Verification Module

The verification workflow is handled by `/verify/<int:file_id>`. It:

- ensures the file belongs to the logged-in user,
- decrypts the stored hash when needed,
- hashes the comparison file,
- determines whether the result is `match` or `mismatch`,
- inserts a record into `verification_logs`,
- stores a short-lived feedback payload in session,
- renders the verification result.

### 11.6 History Module

The `/history/<int:file_id>` route loads verification log entries for a tracked file and renders them as timeline items in `history.html`. This module preserves the audit trail even when recent history is hidden from the main verify page.

### 11.7 Hash Utility Module: `utils/hash_utils.py`

This module contains two functions:

- `generate_file_hash(file_stream, chunk_size=4096)`
- `shorten_hash(hash_value, visible_chars=6)`

The hashing function is written to preserve stream position when possible, making it safe for file-like objects.

### 11.8 Encryption Utility Module: `utils/encryption.py`

This module controls optional encryption. Its responsibilities include:

- reading encryption-related environment variables,
- validating configuration,
- creating a cached Fernet cipher,
- encrypting hashes before storage,
- decrypting hashes before comparison or display.

### 11.9 Presentation Module

The presentation layer is split into:

- `templates/base.html`
- `templates/login.html`
- `templates/register.html`
- `templates/dashboard.html`
- `templates/upload.html`
- `templates/verify.html`
- `templates/history.html`
- `static/css/styles.css`
- `static/js/app.js`

### 11.10 Supporting Helper Functions

The application also includes small but important helpers:

- `current_timestamp()` for uniform time formatting,
- `validate_uploaded_file()` for upload validation,
- `get_user_file()` for ownership enforcement,
- `status_meta()` for dashboard badges,
- `build_verification_feedback()` for normalized result display.

---

## 12. Database Design

### 12.1 Overview

The database is designed to be compact, normalized, and sufficient for an authenticated file tracking workflow. The schema uses foreign keys and indexes to maintain relational integrity and improve query performance.

### 12.2 Entity Relationship Summary

```text
users (1) ---- (many) files (1) ---- (many) verification_logs
```

### 12.3 Table: `users`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | INTEGER | Primary Key, Auto Increment | Unique identifier for a user |
| `username` | TEXT | Not Null, Unique | Login name selected by the user |
| `password` | TEXT | Not Null | Password hash generated by Werkzeug |
| `created_at` | TEXT | Not Null, Default Current Timestamp | Account creation timestamp |

Purpose:

- stores authenticated users,
- prevents duplicate usernames,
- separates identity from tracked file data.

### 12.4 Table: `files`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | INTEGER | Primary Key, Auto Increment | Unique file tracking record |
| `user_id` | INTEGER | Not Null, Foreign Key | Owner of the tracked file |
| `file_name` | TEXT | Not Null | Sanitized filename |
| `hash_value` | TEXT | Not Null | Stored SHA-256 hash or encrypted equivalent |
| `upload_time` | TEXT | Not Null | Time the file was registered |

Purpose:

- stores trusted file fingerprints,
- links each record to a single user,
- supports dashboard inventory and verification selection.

### 12.5 Table: `verification_logs`

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | INTEGER | Primary Key, Auto Increment | Unique verification event |
| `file_id` | INTEGER | Not Null, Foreign Key | Related tracked file |
| `old_hash` | TEXT | Not Null | Stored trusted hash at verification time |
| `new_hash` | TEXT | Not Null | Newly generated hash from comparison file |
| `result` | TEXT | Not Null, Check (`match`, `mismatch`) | Verification outcome |
| `timestamp` | TEXT | Not Null | Verification event time |

Purpose:

- preserves an audit trail,
- supports history reporting,
- retains both compared hashes for review.

### 12.6 Foreign Key Design

- `files.user_id` references `users.id` with `ON DELETE CASCADE`
- `verification_logs.file_id` references `files.id` with `ON DELETE CASCADE`

This ensures referential integrity and automatic cleanup when parent records are removed.

### 12.7 Indexing Strategy

The schema defines:

- `idx_files_user_id`
- `idx_logs_file_id`

These indexes optimize:

- dashboard queries by user,
- history queries by file.

### 12.8 Normalization

The design is close to Third Normal Form:

- user data is stored separately from file records,
- file records are stored separately from verification events,
- repeated verification information is not duplicated in the `files` table,
- the latest result is derived through query logic rather than denormalized storage.

### 12.9 Database Design Merits

- simple enough for teaching,
- relationally correct,
- auditable,
- easy to migrate to a larger RDBMS later.

---

## 13. Algorithm: SHA-256 Hashing

### 13.1 Why SHA-256

SHA-256 is part of the SHA-2 family standardized by NIST [1]. It produces a 256-bit digest, usually represented as a 64-character hexadecimal string. It is widely used for integrity verification because:

- it is deterministic,
- it is efficient,
- it has strong resistance to practical collision attacks,
- it is supported by Python's standard library.

### 13.2 Conceptual Working of SHA-256

At a theoretical level, SHA-256 operates as follows:

1. The input message is padded.
2. The padded message is divided into 512-bit blocks.
3. Initial hash values are loaded.
4. Each block is expanded into a message schedule.
5. The algorithm performs 64 compression rounds using bitwise operations and constants.
6. The intermediate state is updated after each block.
7. The final 256-bit digest is produced.

This design ensures that a very small input change causes a substantially different output digest, which is exactly what integrity verification requires.

### 13.3 Project-Specific Hashing Strategy

In this project, SHA-256 is used through Python's `hashlib.sha256()` implementation. The file is not read into memory all at once. Instead, it is processed in chunks of 4096 bytes.

Benefits of chunk-based hashing:

- lower memory usage,
- suitability for larger files,
- consistent performance,
- better scalability than whole-file reads.

### 13.4 Pseudocode for File Hash Generation

```text
FUNCTION generate_file_hash(file_stream, chunk_size):
    IF chunk_size <= 0:
        RAISE error

    hasher <- SHA256()
    remember stream position if seekable
    move stream to beginning if possible

    LOOP:
        chunk <- read chunk_size bytes
        IF chunk is empty:
            BREAK
        update hasher with chunk

    restore original stream position if needed
    RETURN hexadecimal digest
```

### 13.5 Pseudocode for Verification

```text
FUNCTION verify(trusted_hash, uploaded_file):
    new_hash <- generate_file_hash(uploaded_file, 4096)

    IF new_hash == trusted_hash:
        result <- "match"
        message <- "File Verified - No Changes Detected"
    ELSE:
        result <- "mismatch"
        message <- "Warning: File Modified"

    store verification event in log
    RETURN result, message
```

### 13.6 Role of Hash Shortening

The helper `shorten_hash()` is used only for UI display. It keeps the first and last six characters visible and inserts ellipsis in the middle. The full hash remains stored internally; shortening is purely a readability feature.

### 13.7 Algorithmic Suitability

For this project, SHA-256 is appropriate because it offers a strong security-to-complexity ratio. It is much stronger than legacy alternatives while remaining easy to implement and explain in an academic setting.

---

## 14. Technology Stack

### 14.1 Backend

#### Python 3.11

Python was selected for its readability, broad library ecosystem, and suitability for rapid web application development.

#### Flask 3.1

Flask provides lightweight routing, session handling, template rendering, and extension-friendly design. Its minimalism makes the control flow easy to explain in an academic report.

#### Werkzeug

Werkzeug provides secure password hashing helpers and filename sanitization. In this project it is used for:

- `generate_password_hash`
- `check_password_hash`
- `secure_filename`

### 14.2 Database

#### SQLite

SQLite was chosen because it:

- requires no external server,
- integrates directly with Python,
- supports relational queries and indexes,
- is ideal for academic and small deployment scenarios.

### 14.3 Cryptography

#### `hashlib`

Used for SHA-256 hash generation.

#### `cryptography`

Used for optional Fernet-based encryption of stored hash values.

### 14.4 Frontend

#### HTML with Jinja2

Templates are server-rendered and dynamic values are inserted using Jinja2.

#### CSS

The shared stylesheet defines the visual identity, responsive layout, card-based components, buttons, tables, and status styling.

#### JavaScript

A small script improves usability by:

- auto-dismissing alerts,
- allowing manual alert dismissal,
- previewing selected file names and approximate size.

### 14.5 Deployment

#### Gunicorn

Used as the production WSGI server for deployment.

#### Render

The repository includes `Procfile` and `runtime.txt`, which align with Render deployment expectations.

### 14.6 Why This Stack Was Appropriate

The stack is well suited to the project's goals because it balances:

- implementation simplicity,
- sufficient security features,
- portability,
- learning value,
- deployment readiness.

---

## 15. UI Design

### 15.1 Design Goals

The UI is designed to be:

- clean,
- minimal,
- professional,
- readable,
- responsive,
- task oriented.

### 15.2 Shared Layout

The shared base template provides:

- a minimal application header with the title "IntegrityVault",
- a short subtitle "File Integrity Verification System",
- a consistent page container,
- flash alert rendering,
- a responsive visual shell across pages.

### 15.3 Login Page

The login page intentionally opens directly to the form card. It avoids unnecessary hero content and large mobile spacing. The page contains:

- username field,
- password field,
- login button,
- link to the registration page.

### 15.4 Register Page

The register page follows the same compact pattern as the login page. It includes:

- username field,
- password field,
- confirm password field,
- create account button,
- link back to the login page.

### 15.5 Dashboard Page

The dashboard is the operational center of the application. It includes:

- a toolbar,
- three summary statistic cards,
- a tracked file table,
- action buttons for verification,
- empty-state messaging when no files are present.

The statistics grid uses three columns on large screens, two on tablets, and one on narrow devices.

### 15.6 Upload Page

The upload page uses a single card layout for a focused workflow. The page presents:

- a short description of hashing behavior,
- a custom file picker,
- a button to generate and save the trusted fingerprint.

### 15.7 Verify Page

The verify page is arranged as a two-column layout on larger screens and a stacked layout on mobile devices. It shows:

- tracked file name,
- upload timestamp,
- stored hash,
- comparison file input,
- verify button,
- result banner.

The client-facing verify page currently hides the embedded recent-history panel, but backend verification logging remains active.

### 15.8 History Page

The history page renders verification events as a timeline view. Each record shows:

- timestamp,
- result message,
- stored hash snapshot,
- newly generated hash snapshot.

### 15.9 Responsive Design

The stylesheet includes breakpoints at:

- 1200px,
- 992px,
- 768px,
- 576px.

Responsive strategies include:

- grid collapse from multi-column to single-column layouts,
- reduced padding on smaller devices,
- full-width buttons on small screens,
- horizontal scroll handling for tables,
- stacked actions on narrow layouts.

### 15.10 UI Quality Observations

The interface avoids storing or displaying full raw content. It focuses on concise status communication, especially through the two primary integrity outcomes:

- "File Verified - No Changes Detected"
- "Warning: File Modified"

---

## 16. Implementation Details

### 16.1 Application Initialization

At startup, the application resolves key paths:

- `BASE_DIR`
- `TEMPLATES_DIR`
- `STATIC_DIR`
- `DATABASE_PATH`

It then initializes Flask with explicit template and static folder paths. Configuration values are assigned through environment variables with defaults where appropriate.

### 16.2 Important Runtime Configuration

| Configuration | Current Value / Behavior |
| --- | --- |
| `SECRET_KEY` | Loaded from environment, otherwise fallback value |
| `DATABASE` | Derived from `DATABASE_PATH` |
| `MAX_CONTENT_LENGTH` | 50 MB |
| `HASH_CHUNK_SIZE` | 4096 bytes |
| `SESSION_COOKIE_HTTPONLY` | Enabled |
| `SESSION_COOKIE_SAMESITE` | `Lax` |

### 16.3 User Loading Before Each Request

The `load_logged_in_user()` hook reads `session["user_id"]` when present and populates `g.user`. This makes the current user available across routes and templates.

### 16.4 Route Protection

The `login_required` decorator blocks unauthorized access to protected routes. If a guest accesses a protected page, the application flashes an error and redirects to `/login`.

### 16.5 Registration Logic

The registration route validates:

- username pattern using a regular expression,
- minimum password length,
- password confirmation match,
- uniqueness of username.

If validation passes, the password is hashed and inserted into the `users` table.

### 16.6 Login Logic

The login route:

- reads username and password from the form,
- fetches the matching user record,
- verifies the password using Werkzeug,
- clears existing session state,
- stores the authenticated `user_id`,
- redirects to the dashboard.

### 16.7 Dashboard Query Logic

The dashboard query joins files with the latest verification event using a subquery. This avoids storing redundant status fields inside the `files` table and instead derives the latest known status dynamically.

The route calculates:

- total number of tracked files,
- number of files whose latest check matched,
- number of files whose latest check mismatched.

### 16.8 Upload Handling

The `validate_uploaded_file()` function ensures:

- a file was actually submitted,
- the filename is non-empty after sanitization.

During upload:

- the file stream is hashed,
- the resulting hash may be encrypted,
- only metadata and hash are stored,
- the original file is not permanently retained.

### 16.9 Verification Logic

The verification route is a key part of the implementation. Its sequence is:

1. Load the tracked file using `get_user_file()`.
2. Decrypt the stored hash if encryption is enabled.
3. On POST, validate the uploaded comparison file.
4. Generate a new SHA-256 hash.
5. Compare new hash with trusted hash.
6. Determine `match` or `mismatch`.
7. Insert a verification log entry with old hash, new hash, result, and timestamp.
8. Store a feedback payload in session.
9. Redirect back to the same verify page.
10. On GET, display the result banner using session feedback.

This redirect-after-post pattern improves UX and avoids accidental form resubmission.

### 16.10 Verification History Retrieval

The verify route still queries the latest five verification log entries and prepares `recent_history`, even though the visible history block is currently hidden in the verify template. This is important because the backend logic remains intact and can be restored in the UI later.

### 16.11 History Page Logic

The history route retrieves every verification event for the selected file, orders them by timestamp and ID descending, and renders them with result-specific messaging.

### 16.12 Error Handling

An error handler for HTTP 413 returns a friendly flash message when the file exceeds the 50 MB maximum size.

Other user-facing validation is handled through flash messages such as:

- invalid username,
- duplicate username,
- password mismatch,
- missing file,
- invalid login,
- unauthorized access redirection.

### 16.13 Frontend Behavior

The JavaScript file `static/js/app.js` implements two small but useful enhancements:

1. flash alerts disappear automatically after a delay and can also be dismissed manually,
2. file inputs show the selected filename and approximate size.

### 16.14 Code Maintainability

The codebase demonstrates maintainability through:

- focused helper functions,
- clear route names,
- readable database queries,
- separation of hashing and encryption into utility modules,
- centralized template structure,
- environment-driven deployment settings.

---

## 17. Testing

### 17.1 Testing Objective

The purpose of testing was to verify that the core functional flows of the application behave correctly and that the system remains stable after UI and documentation updates.

### 17.2 Testing Approach

Because the repository currently does not include a dedicated automated unit test suite, testing was performed through:

- code compilation checks,
- Flask test-client smoke testing,
- manual logic inspection of routes and templates,
- verification of expected redirect and response behavior.

### 17.3 Test Environment

| Parameter | Value |
| --- | --- |
| Language | Python 3.11 |
| Framework | Flask 3.1.3 |
| Database | SQLite |
| App Server for Production | Gunicorn 23.0.0 |
| Local Validation Method | Flask test client and compile check |

### 17.4 Smoke Tests Performed

The following validation was executed against a temporary SQLite database using the Flask test client:

| Test Case ID | Scenario | Expected Outcome | Observed Result |
| --- | --- | --- | --- |
| TC-01 | Access `/` as guest | Redirect to `/login` | Pass |
| TC-02 | Register a new user | Success message and login prompt | Pass |
| TC-03 | Log in with valid credentials | Dashboard loads | Pass |
| TC-04 | Upload a file for tracking | File record saved and success message shown | Pass |
| TC-05 | Verify with identical file content | Match result displayed | Pass |
| TC-06 | Verify with modified file content | Mismatch warning displayed | Pass |
| TC-07 | Open history route for tracked file | Verification history page loads | Pass |

### 17.5 Build Validation

The following build validation was also run:

```text
python -m compileall app.py
```

This completed successfully, confirming that the main application module compiles.

### 17.6 Testing Interpretation

The executed tests confirm that the principal business flows are operational:

- authentication works,
- file registration works,
- SHA-256 comparison works,
- mismatch detection works,
- history retrieval works.

### 17.7 Areas for Future Test Expansion

To strengthen quality assurance, future versions should add:

- unit tests for helper functions,
- route tests for invalid input cases,
- authorization tests for cross-user access attempts,
- UI snapshot tests,
- performance tests for larger files,
- deployment health checks.

---

## 18. Results

### 18.1 Functional Outcome

The application successfully achieves its main purpose: it can register a trusted file fingerprint and later determine whether another uploaded file is identical in content to the registered version.

### 18.2 Observed User-Level Results

The project produces clear user-facing outcomes:

- successful login redirects to the dashboard,
- successful upload records a tracked file,
- a matching comparison shows `File Verified - No Changes Detected`,
- a non-matching comparison shows `Warning: File Modified`,
- history records are preserved in `verification_logs`.

### 18.3 Interface Outcome

The user interface is operational across:

- login,
- registration,
- dashboard,
- upload,
- verify,
- history.

The system also includes responsive layout adjustments for smaller screens.

### 18.4 Storage Outcome

The database persists:

- user accounts,
- tracked file metadata,
- trusted hashes,
- verification history.

The design avoids permanent storage of uploaded file content, which keeps storage overhead low.

### 18.5 Demonstrated Capabilities

The project demonstrates the following academic and practical capabilities:

- applied cryptographic hashing,
- secure password storage,
- route-level access control,
- relational schema design,
- server-rendered responsive UI,
- deployable Flask architecture.

### 18.6 Result Summary

Overall, the implemented system satisfies the project's intended outcome and provides a strong academic demonstration of integrity verification using modern web development practices.

---

## 19. Deployment

### 19.1 Local Deployment

The project can be run locally using:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The application then runs on:

```text
http://127.0.0.1:5000
```

### 19.2 Production-Oriented Deployment

The repository includes:

- `Procfile`
- `runtime.txt`
- `requirements.txt`

These support cloud deployment, particularly on Render.

### 19.3 Render Deployment Flow

1. Push the repository to GitHub.
2. Create a Render Web Service.
3. Connect the repository.
4. Set the build command:

```bash
pip install -r requirements.txt
```

5. Set the start command:

```bash
gunicorn app:app
```

6. Set environment variables:

- `SECRET_KEY`
- `ENABLE_HASH_ENCRYPTION`
- `HASH_ENCRYPTION_KEY`
- `DATABASE_PATH`

7. If long-term persistence is needed, mount a persistent disk and point `DATABASE_PATH` to it.

### 19.4 Environment Variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Secures Flask sessions |
| `ENABLE_HASH_ENCRYPTION` | Enables encrypted storage of hashes when `true` |
| `HASH_ENCRYPTION_KEY` | Required when encryption is enabled |
| `DATABASE_PATH` | Controls the SQLite file location |

### 19.5 Deployment Considerations

For serious production use, the deployment should also include:

- HTTPS,
- secure cookie enforcement,
- persistent storage,
- secret management,
- monitoring and backup strategies.

---

## 20. Security Features

### 20.1 Password Hashing

Passwords are not stored in plain text. They are hashed using Werkzeug helpers before being saved in the database.

### 20.2 Session-Based Authentication

Authentication state is stored using Flask sessions. Protected routes are guarded by the `login_required` decorator.

### 20.3 Authorization by Ownership

The function `get_user_file()` ensures that only the owner of a tracked file can access its verification or history route. Unauthorized cross-user access results in a 404 response.

### 20.4 Strong File Integrity Primitive

The system uses SHA-256 instead of weaker legacy checksum algorithms, improving confidence in comparison results.

### 20.5 Filename Sanitization

Uploaded filenames are sanitized with `secure_filename()` to reduce the risk of unsafe path-like input handling.

### 20.6 File Size Restriction

The application limits upload size to 50 MB using `MAX_CONTENT_LENGTH`, which reduces abuse and resource exhaustion risk.

### 20.7 Cookie Hardening

The configuration enables:

- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = "Lax"`

These settings provide basic protection against certain classes of session misuse.

### 20.8 Optional Hash Encryption

When enabled, stored hash values are encrypted using Fernet-based symmetric encryption. Startup validation ensures that encryption cannot be turned on without a valid key.

### 20.9 Audit Trail

Each verification attempt is stored in `verification_logs`, providing an audit-oriented record of prior checks.

### 20.10 Security Gaps Still Present

The project is security-aware but not security-complete. Notable missing controls include:

- CSRF protection,
- brute-force rate limiting,
- account lockout,
- secure cookie flag enforcement under HTTPS,
- formal logging and monitoring integration.

---

## 21. Advantages

1. Simple and focused workflow for integrity verification
2. Strong SHA-256 based comparison method
3. Clean separation of users, files, and verification logs
4. No need to retain uploaded binaries permanently
5. Lightweight deployment with Flask and SQLite
6. Optional encrypted storage for hashes
7. Responsive UI suitable for multiple devices
8. Clear academic value across security, web, and database topics
9. Easy to extend into a larger enterprise or research project

---

## 22. Limitations

1. The application currently uses SQLite, which is not ideal for high-concurrency enterprise deployments.
2. There is no dedicated automated test suite in the repository yet.
3. The default secret key fallback in code must be overridden in real production environments.
4. CSRF protection is not currently implemented.
5. There is no admin module or role-based access control.
6. There is no password recovery or e-mail verification flow.
7. Uploaded file content is not stored, which is efficient but prevents later content retrieval or forensic review from the system itself.
8. The client-facing verify page hides embedded recent-history UI, so history visibility depends on the dedicated route.
9. The system is designed for file comparison, not continuous background monitoring of directories.

---

## 23. Future Enhancements

### 23.1 Database Upgrades

- migrate from SQLite to PostgreSQL for stronger multi-user scalability,
- add migration tooling,
- support backups and replication strategy.

### 23.2 Security Enhancements

- add CSRF protection,
- add rate limiting and failed-login throttling,
- enable secure cookies under HTTPS,
- add password reset and stronger account recovery,
- support multi-factor authentication.

### 23.3 Functional Enhancements

- add REST APIs for automation,
- add file deletion and archival actions,
- add tagging, search, and filtering,
- add version grouping for same-name files,
- export verification reports as PDF or CSV,
- add e-mail alerts on mismatch detection.

### 23.4 Platform Enhancements

- Dockerize the application,
- add CI/CD checks,
- add health endpoints and monitoring,
- integrate cloud object storage if file retention becomes necessary.

### 23.5 Usability Enhancements

- richer dashboard analytics,
- improved history filters,
- downloadable audit logs,
- accessibility review and refinement.

---

## 24. Conclusion

The File Integrity Verification System is a focused and meaningful web application that demonstrates how cryptographic hashing can be used to solve a real integrity problem in a practical and user-friendly way. The system does more than compute checksums: it integrates authentication, per-user ownership, verification logging, optional encrypted storage, responsive design, and deployment readiness into a coherent workflow.

From an academic perspective, the project successfully combines several important disciplines:

- cybersecurity through integrity verification,
- software engineering through modular design,
- database systems through relational modeling,
- web development through Flask and Jinja templates,
- secure coding through password hashing and route protection.

The implemented system is especially strong as a teaching and demonstration project because its architecture is understandable while still reflecting real-world concerns such as session security, validation, audit records, and cloud deployment. At the same time, the project leaves room for future growth into a larger platform with stronger security controls, richer analytics, and broader integration capabilities.

In conclusion, the project meets its intended objective of providing a practical, lightweight, and secure file integrity verification platform. It is suitable both as a complete academic submission and as a strong base for future enhancement.

---

## 25. References

1. National Institute of Standards and Technology. *FIPS PUB 180-4: Secure Hash Standard (SHS).* NIST.
2. Eastlake, D., and Hansen, T. *US Secure Hash Algorithms (SHA and SHA-based HMAC and HKDF).* RFC 6234. IETF.
3. Pallets. *Flask Documentation.* Available from: https://flask.palletsprojects.com/
4. Pallets. *Werkzeug Documentation.* Available from: https://werkzeug.palletsprojects.com/
5. SQLite Consortium. *SQLite Documentation.* Available from: https://www.sqlite.org/docs.html
6. The Cryptography Developers. *Cryptography Documentation: Fernet.* Available from: https://cryptography.io/en/latest/fernet/
7. Render. *Render Documentation.* Available from: https://render.com/docs
8. OWASP Foundation. *OWASP Cheat Sheet Series.* Available from: https://cheatsheetseries.owasp.org/
