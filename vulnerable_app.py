# ============================================================
#  VULNERABLE FLASK APP
#  This file contains intentional security vulnerabilities
#  Created for: Internship Task 3 — Secure Coding Review
#  WARNING: Never use this code in a real project!
# ============================================================

from flask import Flask, request
import sqlite3

app = Flask(__name__)

# ❌ VULNERABILITY 1: Hardcoded Secret Key (CWE-321)
# The secret key is written directly in code.
# Anyone who sees this file (e.g. on GitHub) can forge sessions.
app.secret_key = "mysecretkey123"


# -------------------------------------------------------
# Database Setup
# -------------------------------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    conn.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()


# -------------------------------------------------------
# HOME PAGE
# -------------------------------------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Vulnerable App</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; background: #fff5f5; }
            h1 { color: #c0392b; }
            h2 { color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 4px solid #e74c3c; }
            input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; width: 220px; }
            button { padding: 8px 16px; background: #e74c3c; color: white; border: none;
                     border-radius: 4px; cursor: pointer; margin-top: 5px; }
            code { background: #fdecea; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
            .tag { background: #fadbd8; color: #c0392b; padding: 3px 10px;
                   border-radius: 3px; font-size: 12px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>❌ Vulnerable Flask App — Security Audit Demo</h1>
        <p>This app contains <strong>intentional vulnerabilities</strong> for educational purposes only.</p>

        <!-- SQL INJECTION -->
        <div class="card">
            <span class="tag">🔴 CRITICAL — SQL Injection (CWE-89)</span>
            <h2>1. SQL Injection</h2>
            <p><strong>What happens:</strong> User input is directly added into the SQL query.
               An attacker can bypass login without knowing the password.</p>
            <p><strong>Attack already filled:</strong> Username = <code>admin' OR '1'='1' --</code> | Password = anything</p>
            <form action="/login-vuln" method="POST">
                <input type="text" name="username" value="admin' OR '1'='1' --"><br>
                <input type="password" name="password" value="wrongpassword"><br>
                <button type="submit">❌ Test Vulnerable Login</button>
            </form>
        </div>

        <!-- XSS -->
        <div class="card">
            <span class="tag">🟠 HIGH — Cross Site Scripting (CWE-79)</span>
            <h2>2. XSS — Cross Site Scripting</h2>
            <p><strong>What happens:</strong> User input is placed directly into HTML.
               An attacker can inject JavaScript that runs in the browser.</p>
            <p><strong>Attack already filled:</strong> A script tag in the name field</p>
            <form action="/hello-vuln" method="GET">
                <input type="text" name="name" value="<script>alert('XSS Attack!')</script>"><br>
                <button type="submit">❌ Test Vulnerable XSS</button>
            </form>
        </div>

        <!-- PLAINTEXT PASSWORD -->
        <div class="card">
            <span class="tag">🟠 HIGH — Plaintext Password Storage (CWE-256)</span>
            <h2>3. Plaintext Password Storage</h2>
            <p><strong>What happens:</strong> Password is saved in the database exactly as typed — no encryption.
               If database leaks, all passwords are exposed.</p>
            <form action="/register-vuln" method="POST">
                <input type="text" name="username" placeholder="Enter any username"><br>
                <input type="password" name="password" placeholder="Enter any password"><br>
                <button type="submit">❌ Test Vulnerable Register</button>
            </form>
        </div>

        <!-- EVAL RCE -->
        <div class="card">
            <span class="tag">🔴 CRITICAL — Remote Code Execution (CWE-95)</span>
            <h2>4. Remote Code Execution via eval()</h2>
            <p><strong>What happens:</strong> User input goes directly into Python's eval().
               An attacker can run any command on the server.</p>
            <p><strong>Try this attack:</strong> Type <code>__import__('os').getcwd()</code> and see server path appear</p>
            <form action="/calc-vuln" method="POST">
                <input type="text" name="expression" value="2+2"><br>
                <button type="submit">❌ Test Vulnerable Calculator</button>
            </form>
        </div>

    </body>
    </html>
    """


# -------------------------------------------------------
# VULNERABLE ROUTES
# -------------------------------------------------------

@app.route("/login-vuln", methods=["POST"])
def login_vuln():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")

    # ❌ WRONG — user input directly joined into SQL string
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

    try:
        user = conn.execute(query).fetchone()
        conn.close()
        if user:
            result = f"✅ LOGIN SUCCESS! Logged in as: {user[1]} — SQL Injection worked!"
            color = "#e74c3c"
        else:
            result = "Login failed."
            color = "#7f8c8d"
    except Exception as e:
        result = f"Database Error: {str(e)}"
        color = "#7f8c8d"

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>SQL Injection Result</h2>
        <div style="background:{color}; color:white; padding:15px; border-radius:8px; margin-bottom:15px;">
            {result}
        </div>
        <p><strong>Actual query that ran on database:</strong></p>
        <code style="background:#fdecea; padding:10px; display:block; border-radius:6px; word-break:break-all;">{query}</code>
        <br><a href="/">← Go Back</a>
    </div>
    """


@app.route("/hello-vuln", methods=["GET"])
def hello_vuln():
    name = request.args.get("name", "Guest")

    # ❌ WRONG — raw user input placed directly inside HTML
    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>XSS Vulnerable Result</h2>
        <div style="background:#fadbd8; padding:15px; border-radius:8px;">
            <p>Hello, {name}!</p>
            <p><em>If an alert box appeared above — XSS attack worked!</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


@app.route("/register-vuln", methods=["POST"])
def register_vuln():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

    # ❌ WRONG — password being printed in logs
    print(f"[LOG] New user: {username} / {password}")

    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Vulnerable Register Result</h2>
        <div style="background:#fadbd8; padding:15px; border-radius:8px;">
            <p>❌ This is what got saved in the database:</p>
            <code style="display:block; padding:10px; background:#fdecea; border-radius:6px;">
                Username: {username} &nbsp;|&nbsp; Password: {password}
            </code>
            <p><em>Password is fully visible — no encryption at all!</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


@app.route("/calc-vuln", methods=["POST"])
def calc_vuln():
    expression = request.form["expression"]

    try:
        # ❌ WRONG — never pass user input to eval()
        result = eval(expression)
        msg = f"Result: {result}"
        note = "eval() ran it directly. Attacker can run any Python code on your server!"
    except Exception as e:
        msg = f"Error: {str(e)}"
        note = "An error occurred."

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Vulnerable Calculator Result</h2>
        <div style="background:#fadbd8; padding:15px; border-radius:8px;">
            <p>Expression entered: <code>{expression}</code></p>
            <p><strong>{msg}</strong></p>
            <p><em>❌ {note}</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


if __name__ == "__main__":
    init_db()
    print("\n❌ Vulnerable App running at: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
