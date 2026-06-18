# 🔐 Task 3 — Secure Coding Review
### Internship Project | Python Flask | Security Audit

---

## 📁 Files in This Repository

| File | Description |
|---|---|
| `vulnerable_app.py` | ❌ Flask app with 4 intentional security vulnerabilities |
| `secure_app.py` | ✅ Same app with all vulnerabilities fixed |
| `README.md` | Full documentation of findings and fixes |

---

## 🚀 How to Run

**Step 1 — Install dependencies:**
```bash
pip install flask werkzeug markupsafe
```

**Step 2 — Run the vulnerable app:**
```bash
python vulnerable_app.py
```
Open browser → `http://127.0.0.1:5000`

**Step 3 — Run the secure app (in a new terminal):**
```bash
python secure_app.py
```
Open browser → `http://127.0.0.1:5001`

> Try the same attack on both apps and see the difference!

---

## 🔍 Tools Used for Audit

| Tool | Type | What it does |
|---|---|---|
| **Bandit** | SAST | Scans Python code for security issues automatically |
| **Semgrep** | SAST | Pattern-based scanner using OWASP rules |
| **Safety** | Dependency | Checks for known CVEs in installed packages |
| **OWASP ZAP** | DAST | Simulates attacks on the running application |
| **Manual Review** | Manual | Line-by-line code inspection for logic flaws |

```bash
# Run Bandit scanner
pip install bandit
bandit -r vulnerable_app.py
```

---

## 🚨 Vulnerabilities Found

| # | Severity | Vulnerability | CWE |
|---|---|---|---|
| 1 | 🔴 Critical | SQL Injection | CWE-89 |
| 2 | 🔴 Critical | Remote Code Execution via eval() | CWE-95 |
| 3 | 🟠 High | Cross-Site Scripting (XSS) | CWE-79 |
| 4 | 🟠 High | Plaintext Password Storage | CWE-256 |
| + | 🟡 Medium | Hardcoded Secret Key | CWE-321 |
| + | 🟡 Medium | Password Logged in Plain Text | CWE-532 |
| + | 🔵 Info | Debug Mode Enabled | CWE-94 |

---

## 🔴 Vulnerability 1 — SQL Injection (CWE-89)

**What is it?**
When user input is directly joined into an SQL query, an attacker can break out of it and manipulate the database.

**The Attack:**
```
Username:  admin' OR '1'='1' --
Password:  anything
```
This bypasses login completely — no valid password needed!

**Vulnerable Code:**
```python
# ❌ WRONG — string concatenation
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
```

**Fixed Code:**
```python
# ✅ CORRECT — parameterized query
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

**Why is the fix safe?**
The `?` placeholder keeps user input completely separate from the SQL query. The database treats it as data only, never as part of the command.

---

## 🔴 Vulnerability 2 — Remote Code Execution via eval() (CWE-95)

**What is it?**
Python's `eval()` executes whatever string it receives. If user input reaches `eval()`, the attacker controls the server.

**The Attack:**
```python
# Type this in the calculator field:
__import__('os').getcwd()      # reveals server path
__import__('os').listdir('.')  # lists server files
```

**Vulnerable Code:**
```python
# ❌ WRONG — user input directly in eval()
result = eval(request.form["expression"])
```

**Fixed Code:**
```python
# ✅ CORRECT — AST checker allows only math
import ast
tree = ast.parse(expression, mode="eval")
allowed_nodes = (ast.Expression, ast.BinOp, ast.Add, ast.Sub,
                 ast.Mult, ast.Div, ast.Constant, ast.Num)
for node in ast.walk(tree):
    if not isinstance(node, allowed_nodes):
        raise ValueError("Only math expressions are allowed!")
result = eval(compile(tree, "<string>", "eval"))
```

**Why is the fix safe?**
The AST (Abstract Syntax Tree) parser checks what type of code the expression is. Only math operations are in the allowed list — anything else is blocked before it runs.

---

## 🟠 Vulnerability 3 — XSS (Cross-Site Scripting) (CWE-79)

**What is it?**
When user input is placed directly into HTML without escaping, an attacker can inject JavaScript that runs in other users' browsers.

**The Attack:**
```
Name field:  <script>alert('Hacked!')</script>
```
This script runs in the browser and can steal cookies or redirect users.

**Vulnerable Code:**
```python
# ❌ WRONG — raw input inside HTML
return f"<p>Hello, {name}!</p>"
```

**Fixed Code:**
```python
# ✅ CORRECT — escape() makes HTML tags harmless
from markupsafe import escape
safe_name = escape(name)
return f"<p>Hello, {safe_name}!</p>"
```

**Why is the fix safe?**
`escape()` converts `<script>` into `&lt;script&gt;` — the browser displays it as text, never executes it.

---

## 🟠 Vulnerability 4 — Plaintext Password Storage (CWE-256)

**What is it?**
Storing passwords as plain text means if the database is ever leaked or hacked, every user's password is immediately exposed.

**Vulnerable Code:**
```python
# ❌ WRONG — password saved exactly as typed
db.execute("INSERT INTO users VALUES (?, ?)", (username, password))
# Also wrong — password printed in logs
print(f"Registered: {username} / {password}")
```

**Fixed Code:**
```python
# ✅ CORRECT — hash the password before storing
from werkzeug.security import generate_password_hash
hashed = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
db.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
# Only log the username, never the password
print(f"Registered: {username}")
```

**Why is the fix safe?**
Hashing is a one-way process — the original password cannot be recovered from the hash. Even if the database leaks, attackers only get meaningless hash strings.

---

## ✅ Secure Coding Best Practices

1. **Never trust user input** — always validate length, type, and format
2. **Use parameterized queries** — never concatenate input into SQL
3. **Hash passwords** — use bcrypt or PBKDF2, never store plain text
4. **Escape all output** — prevent XSS by encoding HTML characters
5. **Never use eval()** on user input — use safe parsers instead
6. **Store secrets in environment variables** — never in source code
7. **Never log passwords or tokens** — only log safe, non-sensitive info
8. **Disable debug mode in production** — it exposes server internals

---

## 🗺️ Remediation Plan

| Phase | Timeline | Action |
|---|---|---|
| **Phase 1** | Immediately | Fix SQL Injection, remove eval(), rotate secret key |
| **Phase 2** | Within 2 weeks | Add password hashing, fix XSS, sanitize logs |
| **Phase 3** | Within 1 month | Add Bandit to CI/CD, add rate limiting, full pen test |

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/latest/security/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [CWE Database](https://cwe.mitre.org/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)

---

*Internship Task 3 — Secure Coding Review | Python Flask Application*
