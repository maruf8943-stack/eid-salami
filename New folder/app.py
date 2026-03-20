from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "visitors.db"

# ─── DATABASE SETUP ───────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            age_group  TEXT NOT NULL,
            relation   TEXT NOT NULL,
            ip         TEXT,
            visited_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ─── ROUTES ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/log", methods=["POST"])
def log_visitor():
    data = request.get_json()
    name      = data.get("name", "").strip()
    age_group = data.get("age_group", "")
    relation  = data.get("relation", "")
    ip        = request.headers.get("X-Forwarded-For", request.remote_addr)

    if not name:
        return jsonify({"error": "Name required"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO visitors (name, age_group, relation, ip, visited_at) VALUES (?,?,?,?,?)",
        (name, age_group, relation, ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    # Stats
    total = len(rows)
    young = sum(1 for r in rows if r["age_group"] in ("১০-১৭", "১৮-২৩"))
    adult = sum(1 for r in rows if r["age_group"] == "২৪+")

    return render_template("admin.html", visitors=rows, total=total, young=young, adult=adult)

@app.route("/api/visitors")
def api_visitors():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/clear", methods=["POST"])
def clear_visitors():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM visitors")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    print("\n✅  Server running!")
    print("🌙  Main site  → http://localhost:5000")
    print("📊  Admin page → http://localhost:5000/admin\n")
    app.run(debug=True, host="0.0.0.0", port=5000)