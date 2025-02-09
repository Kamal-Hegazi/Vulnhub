import sqlite3
from flask import Flask, request, render_template, redirect, url_for, send_file, session
import subprocess
import platform

DATABASE = "users.db"
app = Flask(__name__)
app.secret_key = "8573336f852b276fbe9e6576d8a74b84"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Create the users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                username TEXT UNIQUE COLLATE NOCASE, 
                password TEXT, 
                role TEXT DEFAULT 'user'
            )
        """)        

        cursor.execute("SELECT username FROM users WHERE username = ?", ("heath",))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           ("heath", "4155556723", "developer"))
        
        cursor.execute("SELECT username FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           ("admin", "$5fGz8!qL@vXr2P#dT", "admin"))

        conn.commit()

@app.route("/", methods=["GET"])
def index_page():
    return render_template("index.html")

# Robots Page
@app.route('/robots.txt', methods=['GET', 'POST'])
def robots_page():
    return send_file(path_or_file="robots.txt")

# Login Page
@app.route("/bG9naW4", methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user and password == user[2]:
                session["username"] = user[1]
                session["role"] = user[3]

                if session["role"] == "admin":
                    return redirect(url_for("admin_panel"))
                return redirect(url_for("inbox_page"))
            
            return "Invalid credentials! Try again."

    return render_template("login.html")

# Registration Page
@app.route("/cmVnaXN0ZXI", methods=["GET", "POST"])
def registeration_page():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')

        if not username or not password:
            return "Username and password cannot be empty!"
        else:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                return "Username already exists!"
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                return redirect(url_for('login_page'))

    return render_template("register.html")

# Inbox Page (Only accessible after login)
@app.route("/cHJvZmlsZQ", methods=["GET"])
def inbox_page():
    if "username" not in session:
        return redirect(url_for("login_page"))  # Redirect if not logged in

    name = request.args.get("name", session["username"])
    return render_template("inbox.html", name=name)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if session.get("role") != "admin":
        return "<h1>Only Admin Can Access This Resource!<h1>"
    
    output = ""
    full_command = ""

    platform_type = platform.system().lower()

    if request.method == 'POST':
        base_command = request.form.get('base_command', '')
        accepted = ['ping', 'whoami', 'hostname']
        if base_command not in accepted:
            return render_template("admin.html", output="Error: only ping, whoami, and hostname are allowed", full_command=full_command, platform=platform_type)
        user_input = request.form.get('user_input', '').strip()

        is_windows = platform_type == 'windows'

        if base_command == 'ping' and user_input:
            if is_windows:
                full_command = f"ping {user_input}"
            else:
                full_command = f"ping -c 4 {user_input}"

            try:
                result = subprocess.run(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                    timeout=4
                )
                output = result.stdout or result.stderr
            except subprocess.TimeoutExpired:
                output = "Ping command timed out after 4 seconds."
            except Exception as e:
                output = str(e)
        else:
            full_command = base_command
            try:
                result = subprocess.run(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                output = result.stdout or result.stderr
            except Exception as e:
                output = str(e)

    return render_template("admin.html", output=output, full_command=full_command, platform=platform_type)

# Secret Page that Contains Admin Password
@app.route('/c2VjcmV0', methods=['GET'])
def secret_page():
    if session.get("role") != "admin":
        return "<h1>Only Admin Can Access This Resource!<h1>", 403  # Restrict access to admins only
    return ".e^h,Q+r*,W[,Fgi3b#TU+!"  # base92

if __name__ == "__main__":
    init_db()
    print("[!] Database initialized successfully!")
    app.run(host='0.0.0.0', port=80)
