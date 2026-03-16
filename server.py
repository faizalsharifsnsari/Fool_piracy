import hashlib
import json
import sqlite3
import os
import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

DATABASE = "licenses.db"


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():
    return sqlite3.connect(DATABASE)


# -----------------------------
# FINGERPRINT HASH
# -----------------------------
def fingerprint_hash(fp):
    return hashlib.sha256(json.dumps(fp, sort_keys=True).encode()).hexdigest()


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():

    html = """
    <h1>License Activation Server</h1>
    <p>Status: Running</p>

    <h2>Available Endpoints</h2>
    <ul>
        <li>/activate (POST)</li>
        <li>/licenses</li>
        <li>/logs</li>
    </ul>

    <p>This server verifies executable licenses and hardware fingerprints.</p>
    """

    return render_template_string(html)


# -----------------------------
# VIEW LICENSES
# -----------------------------
@app.route("/licenses")
def view_licenses():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM licenses")

    rows = cur.fetchall()
    conn.close()

    html = "<h1>Licenses</h1><table border=1>"
    html += "<tr><th>License</th><th>Exe Hash</th><th>Activation Key</th><th>Fingerprint</th><th>Expiry</th><th>Revoked</th></tr>"

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"

    html += "</table>"

    return html


# -----------------------------
# VIEW ACTIVATION LOGS
# -----------------------------
@app.route("/logs")
def view_logs():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM activation_logs ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()

    html = "<h1>Activation Logs</h1><table border=1>"
    html += "<tr><th>ID</th><th>License</th><th>Fingerprint</th><th>Time</th></tr>"

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"

    html += "</table>"

    return html


# -----------------------------
# ACTIVATE LICENSE
# -----------------------------
@app.route("/activate", methods=["POST"])
def activate():

    data = request.get_json()

    license_key = data.get("license_key")
    exe_hash = data.get("exe_hash")
    hardware = data.get("hardware_profile")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT exe_hash, activation_key, fingerprint_hash, expiry_date, revoked
        FROM licenses
        WHERE license_key=?
        """,
        (license_key,),
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Invalid license key"})

    db_hash, activation_key, stored_fp_hash, expiry_date, revoked = row


    # -----------------------------
    # EXECUTABLE INTEGRITY CHECK
    # -----------------------------
    if exe_hash != db_hash:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Executable integrity check failed. The program file may be modified or corrupted."
        })


    # -----------------------------
    # LICENSE REVOCATION CHECK
    # -----------------------------
    if revoked == 1:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "License has been revoked by the developer"
        })


    # -----------------------------
    # LICENSE EXPIRY CHECK
    # -----------------------------
    if expiry_date:
        today = datetime.datetime.utcnow().date()
        expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()

        if today > expiry:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "License expired"
            })


    current_fp_hash = fingerprint_hash(hardware)


    # -----------------------------
    # FIRST ACTIVATION
    # -----------------------------
    if stored_fp_hash is None:

        cur.execute(
            "UPDATE licenses SET fingerprint_hash=? WHERE license_key=?",
            (current_fp_hash, license_key),
        )

        conn.commit()


    # -----------------------------
    # FUTURE ACTIVATIONS
    # -----------------------------
    else:

        if stored_fp_hash != current_fp_hash:

            conn.close()

            return jsonify({
                "status": "error",
                "message": "License already activated on another device"
            })


    # -----------------------------
    # LOG ACTIVATION
    # -----------------------------
    cur.execute(
        """
        INSERT INTO activation_logs (license_key, fingerprint_hash)
        VALUES (?, ?)
        """,
        (license_key, current_fp_hash),
    )

    conn.commit()
    conn.close()

    return jsonify(
        {
            "status": "activated",
            "activation_key": activation_key,
            "expires_in": 3600
        }
    )


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)