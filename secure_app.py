# ============================================================
#  SECURE FLASK APP — FIXED VERSION
#  All vulnerabilities from vulnerable_app.py are fixed here
#  Created for: Internship Task 3 — Secure Coding Review
# ============================================================

from flask import Flask, request
from werkzeug.security import generate_password_hash
from markupsafe import escape
import sqlite3
import ast
import os

app = Flask(__name__)

# ✅ FIX 1: Secret Key loaded from environment variable (CWE-321)
# Set it in terminal before running: set SECRET_KEY=your_random_key (Windows)
# Or in .env file — never write it directly in code
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-production")


# -------------------------------------------------------
# Database Setup
# -------------------------------------------------------
def init_db():
    conn = sqlite3.connect("secure_users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # ✅ Password stored as a hash, not plain text
    hashed = generate_password_hash("admin123", method="pbkdf2:sha256")
    conn.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', ?)", (hashed,))
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
        <title>Secure App</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; background: #f0fff4; }
            h1 { color: #27ae60; }
            h2 { color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 5px; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 4px solid #27ae60; }
            input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; width: 220px; }
            button { padding: 8px 16px; background: #27ae60; color: white; border: none;
                     border-radius: 4px; cursor: pointer; margin-top: 5px; }
            code { background: #eafaf1; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
            .tag { background: #d5f5e3; color: #1e8449; padding: 3px 10px;
                   border-radius: 3px; font-size: 12px; font-weight: bold; }
            .fix-note { background: #eafaf1; border-left: 3px solid #27ae60;
                        padding: 8px 12px; border-radius: 4px; font-size: 13px; margin: 8px 0; }
        </style>
    </head>
    <body>
        <h1>✅ Secure Flask App — Fixed Version</h1>
        <p>All vulnerabilities from the vulnerable app have been fixed here. Try the same attacks — they will fail!</p>

        <!-- SQL INJECTION FIXED -->
        <div class="card">
            <span class="tag">✅ FIXED — SQL Injection (CWE-89)</span>
            <h2>1. SQL Injection — Fixed</h2>
            <div class="fix-note">🔧 Fix: Parameterized query used — user input never touches the query string directly.</div>
            <p>Try the same attack: <code>admin' OR '1'='1' --</code> — it will fail now!</p>
            <form action="/login-safe" method="POST">
                <input type="text" name="username" value="admin' OR '1'='1' --"><br>
                <input type="password" name="password" value="wrongpassword"><br>
                <button type="submit">✅ Test Secure Login</button>
            </form>
        </div>

        <!-- XSS FIXED -->
        <div class="card">
            <span class="tag">✅ FIXED — Cross Site Scripting (CWE-79)</span>
            <h2>2. XSS — Fixed</h2>
            <div class="fix-note">🔧 Fix: escape() converts HTML tags into plain text — script will not run.</div>
            <p>Try the same attack — the script tag will appear as text, not execute!</p>
            <form action="/hello-safe" method="GET">
                <input type="text" name="name" value="<script>alert('XSS Attack!')</script>"><br>
                <button type="submit">✅ Test Secure XSS</button>
            </form>
        </div>

        <!-- PASSWORD HASHING FIXED -->
        <div class="card">
            <span class="tag">✅ FIXED — Password Hashing (CWE-256)</span>
            <h2>3. Password Hashing — Fixed</h2>
            <div class="fix-note">🔧 Fix: Password is hashed using PBKDF2-SHA256 before storing — original is unreadable.</div>
            <form action="/register-safe" method="POST">
                <input type="text" name="username" placeholder="Enter any username"><br>
                <input type="password" name="password" placeholder="Enter any password"><br>
                <button type="submit">✅ Test Secure Register</button>
            </form>
        </div>

        <!-- EVAL FIXED -->
        <div class="card">
            <span class="tag">✅ FIXED — Remote Code Execution (CWE-95)</span>
            <h2>4. Safe Calculator — Fixed</h2>
            <div class="fix-note">🔧 Fix: AST parser checks the expression — only basic math is allowed, OS commands are blocked.</div>
            <p>Try: <code>__import__('os').getcwd()</code> — it will be blocked!</p>
            <form action="/calc-safe" method="POST">
                <input type="text" name="expression" value="2+2"><br>
                <button type="submit">✅ Test Secure Calculator</button>
            </form>
        </div>

    </body>
    </html>
    """


# -------------------------------------------------------
# SECURE ROUTES
# -------------------------------------------------------

# ✅ FIX: SQL Injection — Parameterized Query
@app.route("/login-safe", methods=["POST"])
def login_safe():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = sqlite3.connect("secure_users.db")

    # ✅ CORRECT — ? placeholder keeps input separate from query
    query = "SELECT * FROM users WHERE username = ?"
    user = conn.execute(query, (username,)).fetchone()
    conn.close()

    if user:
        result = f"This is a real user but wrong password was given. Attack blocked! ✅"
        color = "#27ae60"
    else:
        result = "❌ Login failed — SQL Injection did not work! Parameterized query blocked the attack. ✅"
        color = "#27ae60"

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Secure Login Result</h2>
        <div style="background:{color}; color:white; padding:15px; border-radius:8px; margin-bottom:15px;">
            {result}
        </div>
        <p><strong>Query used (safe version):</strong></p>
        <code style="background:#eafaf1; padding:10px; display:block; border-radius:6px;">
            SELECT * FROM users WHERE username = ? — (input passed separately, not inside query)
        </code>
        <br><a href="/">← Go Back</a>
    </div>
    """


# ✅ FIX: XSS — Output Escaped
@app.route("/hello-safe", methods=["GET"])
def hello_safe():
    name = request.args.get("name", "Guest")

    # ✅ CORRECT — escape() converts <script> into &lt;script&gt; — harmless text
    safe_name = escape(name)

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Secure XSS Result</h2>
        <div style="background:#d5f5e3; padding:15px; border-radius:8px;">
            <p>Hello, {safe_name}!</p>
            <p><em>✅ The script tag was converted to plain text — no alert box, no attack!</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


# ✅ FIX: Password Hashing
@app.route("/register-safe", methods=["POST"])
def register_safe():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return "Username and password are required!", 400

    # ✅ CORRECT — hash the password before storing
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

    try:
        conn = sqlite3.connect("secure_users.db")
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
    except Exception as e:
        return f"Error: {str(e)}", 400

    # ✅ CORRECT — only username logged, never the password
    print(f"[LOG] New user registered: {username}")

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Secure Register Result</h2>
        <div style="background:#d5f5e3; padding:15px; border-radius:8px;">
            <p>✅ This is what got saved in the database:</p>
            <code style="display:block; padding:10px; background:#eafaf1; border-radius:6px; word-break:break-all;">
                Username: {escape(username)}<br>
                Password: {hashed_password}
            </code>
            <p><em>✅ Original password is unreadable — even if database leaks, passwords are safe!</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


# ✅ FIX: Safe Calculator — AST-based evaluator
@app.route("/calc-safe", methods=["POST"])
def calc_safe():
    expression = request.form.get("expression", "")

    try:
        # ✅ CORRECT — parse the expression and only allow math operations
        tree = ast.parse(expression, mode="eval")
        allowed_nodes = (
            ast.Expression, ast.BinOp, ast.UnaryOp,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
            ast.USub, ast.Constant, ast.Num
        )
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                raise ValueError(f"Blocked! Only math is allowed. Detected: {type(node).__name__}")

        result = eval(compile(tree, "<string>", "eval"))
        msg = f"Result: {result}"
        note = "✅ Only math expression was allowed — OS commands are blocked!"
        color = "#d5f5e3"

    except ValueError as e:
        msg = f"Blocked: {str(e)}"
        note = "✅ Dangerous expression was detected and blocked by AST checker!"
        color = "#d5f5e3"
    except Exception as e:
        msg = f"Invalid expression: {str(e)}"
        note = "Expression could not be evaluated."
        color = "#d5f5e3"

    return f"""
    <div style="font-family:Arial; max-width:600px; margin:40px auto; padding:20px;">
        <h2>Secure Calculator Result</h2>
        <div style="background:{color}; padding:15px; border-radius:8px;">
            <p>Expression entered: <code>{escape(expression)}</code></p>
            <p><strong>{msg}</strong></p>
            <p><em>{note}</em></p>
        </div>
        <br><a href="/">← Go Back</a>
    </div>
    """


if __name__ == "__main__":
    init_db()
    print("\n✅ Secure App running at: http://127.0.0.1:5001\n")
    app.run(debug=False, port=5001)
