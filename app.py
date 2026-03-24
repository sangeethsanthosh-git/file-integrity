from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from utils.encryption import (
    decrypt_hash_value,
    encrypt_hash_value,
    validate_encryption_configuration,
)
from utils.hash_utils import generate_file_hash, shorten_hash


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "file_integrity.db")))
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["DATABASE"] = str(DATABASE_PATH)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["HASH_CHUNK_SIZE"] = 4096
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

validate_encryption_configuration()


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def init_db() -> None:
    db = get_db()
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db.executescript(schema)
    db.commit()


@app.teardown_appcontext
def close_db(exception=None) -> None:  # pragma: no cover - Flask lifecycle hook
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    g.user = None

    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


@app.template_filter("short_hash")
def short_hash_filter(hash_value: str | None) -> str:
    return shorten_hash(hash_value)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def validate_uploaded_file(file_storage):
    if file_storage is None:
        return None, "Please choose a file to continue."

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        return None, "Please choose a valid file."

    return filename, None


def get_user_file(file_id: int):
    file_record = get_db().execute(
        """
        SELECT id, user_id, file_name, hash_value, upload_time
        FROM files
        WHERE id = ? AND user_id = ?
        """,
        (file_id, g.user["id"]),
    ).fetchone()

    if file_record is None:
        abort(404)

    return file_record


def status_meta(result: str | None) -> tuple[str, str]:
    if result == "match":
        return "match", "Verified"
    if result == "mismatch":
        return "mismatch", "Modified"
    return "not-checked", "Not Checked"


def build_verification_feedback(file_id: int, result: str, old_hash: str, new_hash: str, timestamp: str):
    matched = result == "match"
    return {
        "file_id": file_id,
        "result": result,
        "message": "File Verified – No Changes Detected" if matched else "Warning: File Modified",
        "old_hash": shorten_hash(old_hash),
        "new_hash": shorten_hash(new_hash),
        "timestamp": timestamp,
    }


@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not USERNAME_PATTERN.fullmatch(username):
            flash(
                "Username must be 3-32 characters and may only use letters, numbers, dots, dashes, and underscores.",
                "error",
            )
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            try:
                get_db().execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                get_db().commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username is already taken.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    file_rows = get_db().execute(
        """
        SELECT
            f.id,
            f.file_name,
            f.hash_value,
            f.upload_time,
            v.result AS last_result,
            v.timestamp AS last_checked
        FROM files AS f
        LEFT JOIN verification_logs AS v
            ON v.id = (
                SELECT id
                FROM verification_logs
                WHERE file_id = f.id
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
            )
        WHERE f.user_id = ?
        ORDER BY f.upload_time DESC, f.id DESC
        """,
        (g.user["id"],),
    ).fetchall()

    files = []
    verified_count = 0
    modified_count = 0

    for row in file_rows:
        status_class, status_text = status_meta(row["last_result"])
        if row["last_result"] == "match":
            verified_count += 1
        elif row["last_result"] == "mismatch":
            modified_count += 1

        files.append(
            {
                "id": row["id"],
                "file_name": row["file_name"],
                "upload_time": row["upload_time"],
                "hash_display": shorten_hash(decrypt_hash_value(row["hash_value"])),
                "status_class": status_class,
                "status_text": status_text,
                "last_checked": row["last_checked"],
            }
        )

    stats = {
        "total_files": len(files),
        "verified_files": verified_count,
        "modified_files": modified_count,
    }

    return render_template("dashboard.html", files=files, stats=stats)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        file_storage = request.files.get("file")
        filename, error = validate_uploaded_file(file_storage)

        if error:
            flash(error, "error")
            return render_template("upload.html")

        hash_value = generate_file_hash(
            file_storage.stream,
            chunk_size=app.config["HASH_CHUNK_SIZE"],
        )

        get_db().execute(
            """
            INSERT INTO files (user_id, file_name, hash_value, upload_time)
            VALUES (?, ?, ?, ?)
            """,
            (
                g.user["id"],
                filename,
                encrypt_hash_value(hash_value),
                current_timestamp(),
            ),
        )
        get_db().commit()

        flash(
            f"File uploaded successfully. Tracked hash: {shorten_hash(hash_value)}.",
            "success",
        )
        return redirect(url_for("dashboard"))

    return render_template("upload.html")


@app.route("/verify/<int:file_id>", methods=["GET", "POST"])
@login_required
def verify_file(file_id: int):
    tracked_file = get_user_file(file_id)
    stored_hash = decrypt_hash_value(tracked_file["hash_value"])

    if request.method == "POST":
        file_storage = request.files.get("file")
        _, error = validate_uploaded_file(file_storage)

        if error:
            flash(error, "error")
            return redirect(url_for("verify_file", file_id=file_id))

        new_hash = generate_file_hash(
            file_storage.stream,
            chunk_size=app.config["HASH_CHUNK_SIZE"],
        )
        result = "match" if new_hash == stored_hash else "mismatch"
        timestamp = current_timestamp()

        get_db().execute(
            """
            INSERT INTO verification_logs (file_id, old_hash, new_hash, result, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                file_id,
                encrypt_hash_value(stored_hash),
                encrypt_hash_value(new_hash),
                result,
                timestamp,
            ),
        )
        get_db().commit()

        feedback = build_verification_feedback(file_id, result, stored_hash, new_hash, timestamp)
        session["verification_feedback"] = feedback
        flash(feedback["message"], "success" if result == "match" else "error")
        return redirect(url_for("verify_file", file_id=file_id))

    feedback = session.pop("verification_feedback", None)
    if feedback and feedback.get("file_id") != file_id:
        session["verification_feedback"] = feedback
        feedback = None

    history_rows = get_db().execute(
        """
        SELECT id, old_hash, new_hash, result, timestamp
        FROM verification_logs
        WHERE file_id = ?
        ORDER BY timestamp DESC, id DESC
        LIMIT 5
        """,
        (file_id,),
    ).fetchall()

    recent_history = [
        {
            "id": row["id"],
            "old_hash": shorten_hash(decrypt_hash_value(row["old_hash"])),
            "new_hash": shorten_hash(decrypt_hash_value(row["new_hash"])),
            "result": row["result"],
            "timestamp": row["timestamp"],
        }
        for row in history_rows
    ]

    return render_template(
        "verify.html",
        tracked_file={
            "id": tracked_file["id"],
            "file_name": tracked_file["file_name"],
            "upload_time": tracked_file["upload_time"],
            "hash_display": shorten_hash(stored_hash),
        },
        feedback=feedback,
        recent_history=recent_history,
    )


@app.route("/history/<int:file_id>")
@login_required
def history(file_id: int):
    tracked_file = get_user_file(file_id)
    history_rows = get_db().execute(
        """
        SELECT id, old_hash, new_hash, result, timestamp
        FROM verification_logs
        WHERE file_id = ?
        ORDER BY timestamp DESC, id DESC
        """,
        (file_id,),
    ).fetchall()

    history_entries = [
        {
            "id": row["id"],
            "old_hash": shorten_hash(decrypt_hash_value(row["old_hash"])),
            "new_hash": shorten_hash(decrypt_hash_value(row["new_hash"])),
            "result": row["result"],
            "result_message": "File Verified – No Changes Detected"
            if row["result"] == "match"
            else "Warning: File Modified",
            "timestamp": row["timestamp"],
        }
        for row in history_rows
    ]

    return render_template(
        "history.html",
        tracked_file={
            "id": tracked_file["id"],
            "file_name": tracked_file["file_name"],
            "upload_time": tracked_file["upload_time"],
            "hash_display": shorten_hash(decrypt_hash_value(tracked_file["hash_value"])),
        },
        history_entries=history_entries,
    )


@app.errorhandler(413)
def file_too_large(error):
    flash("File is too large. Maximum allowed size is 50 MB.", "error")
    destination = request.referrer or url_for("dashboard")
    return redirect(destination)


with app.app_context():
    init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

