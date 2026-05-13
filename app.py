from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import hashlib
from db import get_connection, init_db
from logic import calculate_mttr, calculate_mttd, calculate_mtbf, format_hours, is_valid_incident

app = Flask(__name__)
app.secret_key = "mysecretkey123"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Please fill all fields.")
            return render_template("register.html")
        conn = get_connection()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user:
            flash("This username is already taken.")
            conn.close()
            return render_template("register.html")
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                     (username, hash_password(password)))
        conn.commit()
        conn.close()
        flash("Registration successful. Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Wrong username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    status_filter = request.args.get("status", "all")
    severity_filter = request.args.get("severity", "all")
    conn = get_connection()
    query = "SELECT * FROM incidents WHERE user_id = ?"
    params = [session["user_id"]]
    if status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)
    if severity_filter != "all":
        query += " AND severity = ?"
        params.append(severity_filter)
    query += " ORDER BY detected_at DESC"
    incidents = conn.execute(query, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM incidents WHERE user_id = ?", (session["user_id"],)).fetchone()[0]
    open_count = conn.execute("SELECT COUNT(*) FROM incidents WHERE user_id = ? AND status = 'open'", (session["user_id"],)).fetchone()[0]
    closed_count = conn.execute("SELECT COUNT(*) FROM incidents WHERE user_id = ? AND status = 'closed'", (session["user_id"],)).fetchone()[0]
    stats = {"total": total, "open": open_count, "closed": closed_count}
    conn.close()
    return render_template("dashboard.html", incidents=incidents,
                           status_filter=status_filter, severity_filter=severity_filter,
                           stats=stats)

@app.route("/incident/add", methods=["GET", "POST"])
@login_required
def add_incident():
    if request.method == "POST":
        title = request.form["title"].strip()
        incident_type = request.form["incident_type"]
        severity = request.form["severity"]
        started_at = request.form["started_at"]
        detected_at = request.form["detected_at"]
        action_taken = request.form.get("action_taken", "").strip()
        valid, msg = is_valid_incident(title, incident_type, started_at, detected_at)
        if not valid:
            flash(msg)
            return render_template("add_incident.html")
        conn = get_connection()
        conn.execute(
            "INSERT INTO incidents (user_id, title, incident_type, severity, started_at, detected_at, action_taken, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'open')",
            (session["user_id"], title, incident_type, severity, started_at, detected_at, action_taken)
        )
        conn.commit()
        conn.close()
        flash("Incident added successfully.")
        return redirect(url_for("dashboard"))
    return render_template("add_incident.html")

@app.route("/incident/<int:incident_id>")
@login_required
def incident_detail(incident_id):
    conn = get_connection()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ? AND user_id = ?",
        (incident_id, session["user_id"])
    ).fetchone()
    if not incident:
        conn.close()
        flash("Incident not found.")
        return redirect(url_for("dashboard"))
    mttr = calculate_mttr(incident["detected_at"], incident["resolved_at"])
    mttd = calculate_mttd(incident["started_at"], incident["detected_at"])
    all_incidents = conn.execute(
        "SELECT started_at FROM incidents WHERE user_id = ? AND status = 'closed' ORDER BY started_at ASC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    mtbf = calculate_mtbf([i["started_at"] for i in all_incidents])
    return render_template("detail.html", incident=incident,
                           mttr=format_hours(mttr), mttd=format_hours(mttd), mtbf=format_hours(mtbf))

@app.route("/incident/<int:incident_id>/edit", methods=["GET", "POST"])
@login_required
def edit_incident(incident_id):
    conn = get_connection()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ? AND user_id = ?",
        (incident_id, session["user_id"])
    ).fetchone()
    if not incident:
        conn.close()
        flash("Incident not found.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        title = request.form["title"].strip()
        incident_type = request.form["incident_type"]
        severity = request.form["severity"]
        started_at = request.form["started_at"]
        detected_at = request.form["detected_at"]
        resolved_at = request.form.get("resolved_at") or None
        action_taken = request.form.get("action_taken", "").strip()
        status = request.form["status"]
        valid, msg = is_valid_incident(title, incident_type, started_at, detected_at)
        if not valid:
            flash(msg)
            return render_template("edit_incident.html", incident=incident)
        conn.execute(
            "UPDATE incidents SET title=?, incident_type=?, severity=?, started_at=?, detected_at=?, resolved_at=?, action_taken=?, status=? WHERE id=? AND user_id=?",
            (title, incident_type, severity, started_at, detected_at, resolved_at, action_taken, status, incident_id, session["user_id"])
        )
        conn.commit()
        conn.close()
        flash("Incident updated.")
        return redirect(url_for("incident_detail", incident_id=incident_id))
    conn.close()
    return render_template("edit_incident.html", incident=incident)

@app.route("/incident/<int:incident_id>/delete", methods=["POST"])
@login_required
def delete_incident(incident_id):
    conn = get_connection()
    conn.execute("DELETE FROM incidents WHERE id = ? AND user_id = ?",
                 (incident_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Incident deleted.")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)