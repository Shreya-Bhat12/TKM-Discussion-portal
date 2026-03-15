from flask import Flask, request, redirect, session, render_template_string, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tkm_ntf_secret_2025"

DB_FILE = "model.db"
PER_PAGE = 10

# Toyota logo embedded as base64 - no external file needed
TOYOTA_LOGO = "data:image/png;base64,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"


# -------------------------
# Database helpers
# -------------------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        Sl_No INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'QACAdmin'
    )
    """)
    cur.execute("SELECT COUNT(*) as cnt FROM admins")
    if cur.fetchone()['cnt'] == 0:
        default_admins = [
            ("QAC Admin", "qacadmin", "qac123", "QACAdmin"),
            ("QIC Admin", "qicadmin", "qic123", "QICAdmin"),
            ("Production Admin", "prodadmin", "prod123", "ProductionAdmin"),
        ]
        cur.executemany("INSERT INTO admins(name,username,password,role) VALUES(?,?,?,?)", default_admins)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dealers (
        Sl_No INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        department TEXT DEFAULT 'General'
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        Sl_No INTEGER PRIMARY KEY AUTOINCREMENT,
        dealer_id INTEGER,
        Part_Name TEXT,
        Part_Number TEXT,
        Model TEXT,
        Supplier_name TEXT,
        Date_sent TEXT,
        Customer_Concern TEXT,
        status TEXT DEFAULT 'Open',
        Remark TEXT,
        PIC TEXT,
        category TEXT,
        is_deleted INTEGER DEFAULT 0,
        created_by TEXT,
        created_by_role TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Discussion (
        Sl_No INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id INTEGER,
        pi_number TEXT,
        message TEXT,
        dept TEXT,
        created_at TEXT,
        author_name TEXT,
        author_username TEXT,
        author_role TEXT,
        is_deleted INTEGER DEFAULT 0,
        edited INTEGER DEFAULT 0,
        edited_at TEXT,
        edited_by TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_current_user():
    if 'admin' in session:
        return session.get('admin_name','Admin'), session.get('admin_username','admin'), session.get('admin_role','Admin')
    elif 'dealer' in session:
        return session.get('dealer_name','User'), session.get('dealer_username','user'), session.get('dealer_department','General')
    return 'Unknown', 'unknown', 'Unknown'

# =========================================================
# GLOBAL STYLE — metallic blue theme
# =========================================================
def get_base_style():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --steel-darkest: #0a1628;
    --steel-darker:  #0d1f3c;
    --steel-dark:    #112244;
    --steel-mid:     #1a3a6b;
    --steel-base:    #1e4d8c;
    --steel-light:   #2a6abf;
    --steel-lighter: #3a85e0;
    --steel-pale:    #5ba3f5;
    --steel-frost:   #a8c8f8;
    --steel-ice:     #d4e8ff;
    --chrome-1:      #c8d8e8;
    --chrome-2:      #9ab4cc;
    --chrome-3:      #6a8eaa;
    --accent-gold:   #c8a84b;
    --accent-red:    #c0392b;
    --accent-green:  #1a8a5a;
    --bg-page:       #0e1a2e;
    --bg-card:       #131f33;
    --bg-card2:      #162040;
    --border-light:  rgba(90,140,200,0.25);
    --border-glow:   rgba(58,133,224,0.5);
    --text-main:     #dce8f5;
    --text-muted:    #7a9bbf;
    --text-dim:      #4a6a8a;
    --shadow-blue:   0 4px 20px rgba(26,74,140,0.4);
    --shadow-glow:   0 0 20px rgba(58,133,224,0.2);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'IBM Plex Sans', sans-serif;
    background: var(--bg-page);
    color: var(--text-main);
    min-height: 100vh;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(26,74,140,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(10,30,70,0.3) 0%, transparent 50%);
}

/* ======== HEADER ======== */
.site-header {
    background: linear-gradient(135deg, var(--steel-darkest) 0%, var(--steel-dark) 50%, var(--steel-darker) 100%);
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, transparent, var(--steel-lighter), var(--accent-gold), var(--steel-lighter), transparent) 1;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 30px rgba(0,0,0,0.6);
}

.header-logo-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
}
.header-logo-wrap img {
    height: 44px;
    filter: drop-shadow(0 0 8px rgba(200,168,75,0.4));
}
.header-brand {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
}
.header-brand .brand-main {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--steel-ice);
    letter-spacing: 1px;
    text-transform: uppercase;
}
.header-brand .brand-sub {
    font-size: 0.68rem;
    color: var(--accent-gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}

.header-center-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--steel-frost), var(--steel-ice), var(--accent-gold), var(--steel-ice), var(--steel-frost));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
}

.header-right-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}

.user-pill {
    background: rgba(42,106,191,0.2);
    border: 1px solid var(--border-light);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: var(--steel-frost);
    display: flex;
    align-items: center;
    gap: 6px;
}

.header-nav {
    display: flex;
    align-items: center;
    gap: 2px;
}
.header-nav a {
    color: var(--chrome-2);
    text-decoration: none;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 5px 10px;
    border-radius: 4px;
    transition: all 0.2s;
    letter-spacing: 0.3px;
}
.header-nav a:hover {
    background: rgba(42,106,191,0.3);
    color: var(--steel-ice);
}
.header-nav a.nav-danger { color: #e88; }
.header-nav a.nav-danger:hover { background: rgba(192,57,43,0.25); color: #ffaaaa; }

/* ======== ROLE BADGES ======== */
.role-tag {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    font-family: 'Rajdhani', sans-serif;
}
.role-QACAdmin    { background: linear-gradient(135deg,#1a3a6b,#2a5a9b); color: #a8d8ff; border: 1px solid #2a6abf; }
.role-QICAdmin    { background: linear-gradient(135deg,#0e3a5a,#1a5a7a); color: #a8e8ff; border: 1px solid #1a8ab0; }
.role-ProductionAdmin { background: linear-gradient(135deg,#2a1a5a,#4a2a8a); color: #d8c8ff; border: 1px solid #6a3abf; }
.role-General, .role-dealer, .role-Dealer, .role-QAC, .role-QIC, .role-Production, .role-Supplier {
    background: linear-gradient(135deg,#1a2a3a,#2a3a4a); color: #8ab8d8; border: 1px solid #3a5a7a;
}

/* ======== PAGE / CARD ======== */
.page-wrap { max-width: 1500px; margin: auto; padding: 20px 24px; }

.card {
    background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-card2) 100%);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow: var(--shadow-blue);
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--steel-lighter), transparent);
}

h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.5px;
}
h1 { font-size: 1.6rem; color: var(--steel-ice); }
h2 { font-size: 1.3rem; color: var(--steel-frost); }
h3 { font-size: 1.1rem; color: var(--chrome-2); font-weight: 600; }

/* ======== FORMS ======== */
.form-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

input[type=text], input[type=password], input[type=date], textarea, select {
    padding: 7px 11px;
    background: rgba(10,22,40,0.8);
    border: 1px solid var(--border-light);
    border-radius: 5px;
    color: var(--text-main);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    transition: border 0.2s, box-shadow 0.2s;
}
input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: var(--steel-lighter);
    box-shadow: 0 0 0 3px rgba(58,133,224,0.15);
}
select option { background: var(--steel-darkest); color: var(--text-main); }

.btn {
    display: inline-block;
    padding: 7px 16px;
    border: none;
    border-radius: 5px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.92rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.15s;
}
.btn-primary {
    background: linear-gradient(135deg, var(--steel-mid), var(--steel-base));
    color: var(--steel-ice);
    border: 1px solid var(--steel-light);
    box-shadow: 0 2px 10px rgba(26,74,140,0.4);
}
.btn-primary:hover { background: linear-gradient(135deg, var(--steel-base), var(--steel-lighter)); box-shadow: 0 4px 15px rgba(42,106,191,0.5); }
.btn-success { background: linear-gradient(135deg,#0d5a3a,#1a8a5a); color: #a8ffd8; border: 1px solid #1a8a5a; }
.btn-danger  { background: linear-gradient(135deg,#5a0d0d,#8a1a1a); color: #ffaaaa; border: 1px solid #c0392b; }
.btn-warn    { background: linear-gradient(135deg,#5a3a0d,#8a5a1a); color: #ffd8a8; border: 1px solid #b06820; }
.btn-sm { padding: 3px 9px; font-size: 0.78rem; }

/* ======== TABLE ======== */
.table-wrap { overflow-x: auto; border-radius: 6px; }
table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
thead tr {
    background: linear-gradient(135deg, var(--steel-darkest), var(--steel-dark));
    border-bottom: 2px solid var(--steel-light);
}
th {
    padding: 10px 11px;
    text-align: left;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--chrome-1);
    white-space: nowrap;
}
td {
    padding: 9px 11px;
    border-bottom: 1px solid rgba(42,106,191,0.1);
    color: var(--text-main);
    vertical-align: middle;
}
tr:hover td { background: rgba(42,106,191,0.07); }

.status-Open       { color: #5af0a0; font-weight: 700; font-size: 0.82rem; }
.status-Inprogress { color: #f0c050; font-weight: 700; font-size: 0.82rem; }
.status-Closed     { color: #f07070; font-weight: 700; font-size: 0.82rem; }

/* ======== PAGINATION ======== */
.pagination { display: flex; gap: 5px; margin-top: 14px; flex-wrap: wrap; }
.pagination a {
    padding: 5px 12px;
    border: 1px solid var(--border-light);
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.82rem;
    background: rgba(10,22,40,0.6);
    color: var(--steel-frost);
    transition: all 0.15s;
}
.pagination a:hover { background: rgba(42,106,191,0.25); border-color: var(--steel-light); }
.pagination a.active { background: linear-gradient(135deg,var(--steel-mid),var(--steel-base)); color: white; border-color: var(--steel-lighter); }

/* ======== LOGIN PAGE ======== */
.login-wrap {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 0;
    background:
        radial-gradient(ellipse at 30% 30%, rgba(26,74,140,0.25) 0%, transparent 60%),
        radial-gradient(ellipse at 70% 70%, rgba(10,30,60,0.4) 0%, transparent 60%),
        linear-gradient(160deg, #080f1e 0%, #0d1a30 50%, #0a1222 100%);
}
.login-header-bar {
    width: 100%;
    background: linear-gradient(135deg, var(--steel-darkest), var(--steel-dark));
    border-bottom: 2px solid transparent;
    border-image: linear-gradient(90deg, transparent, var(--steel-lighter), var(--accent-gold), var(--steel-lighter), transparent) 1;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 30px rgba(0,0,0,0.6);
    position: fixed;
    top: 0;
    z-index: 10;
}
.login-content {
    margin-top: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 70px);
    width: 100%;
}
.login-card {
    background: linear-gradient(145deg, rgba(13,31,60,0.95), rgba(18,28,50,0.98));
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 36px 32px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(26,74,140,0.2);
    position: relative;
    overflow: hidden;
}
.login-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--steel-mid), var(--steel-lighter), var(--accent-gold), var(--steel-lighter), var(--steel-mid));
}
.login-logo-area {
    text-align: center;
    margin-bottom: 20px;
}
.login-logo-area img {
    height: 64px;
    filter: drop-shadow(0 0 12px rgba(200,168,75,0.5));
}
.login-title {
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--steel-ice);
    margin-bottom: 4px;
}
.login-subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-light), transparent);
    margin: 14px 0;
}
.field-group { margin-bottom: 14px; }
.field-group label {
    display: block;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.field-group input, .field-group select { width: 100%; }
.pw-wrap { position: relative; }
.pw-wrap input { width: 100%; padding-right: 52px; }
.pw-toggle {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    background: none; border: none; cursor: pointer;
    color: var(--text-muted); font-size: 0.75rem; font-family: inherit;
    padding: 2px 6px; border-radius: 3px;
}
.pw-toggle:hover { color: var(--steel-frost); background: rgba(42,106,191,0.2); }
.login-btn {
    width: 100%;
    padding: 10px;
    margin-top: 8px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: linear-gradient(135deg, var(--steel-mid) 0%, var(--steel-base) 50%, var(--steel-light) 100%);
    color: var(--steel-ice);
    border: 1px solid var(--steel-lighter);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 3px 15px rgba(26,74,140,0.4);
}
.login-btn:hover {
    background: linear-gradient(135deg, var(--steel-base), var(--steel-lighter));
    box-shadow: 0 5px 20px rgba(42,106,191,0.5);
    transform: translateY(-1px);
}
.login-links {
    text-align: center;
    margin-top: 16px;
    font-size: 0.82rem;
    color: var(--text-muted);
}
.login-links a { color: var(--steel-pale); text-decoration: none; }
.login-links a:hover { color: var(--steel-ice); text-decoration: underline; }

/* ======== ALERTS ======== */
.alert {
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 14px;
    font-size: 0.88rem;
}
.alert-info    { background: rgba(26,74,140,0.2); border-left: 3px solid var(--steel-lighter); color: var(--steel-frost); }
.alert-success { background: rgba(26,138,90,0.15); border-left: 3px solid #1a8a5a; color: #5af0a0; }
.alert-danger  { background: rgba(192,57,43,0.15); border-left: 3px solid #c0392b; color: #ffaaaa; }

/* ======== DISCUSSION ======== */
.disc-card {
    background: rgba(10,22,40,0.6);
    border: 1px solid var(--border-light);
    border-left: 3px solid var(--steel-lighter);
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.disc-card.deleted {
    opacity: 0.45;
    border-left-color: var(--text-dim);
    background: rgba(10,14,20,0.4);
}
.disc-meta {
    display: flex; align-items: center; gap: 8px;
    flex-wrap: wrap; margin-bottom: 7px; font-size: 0.78rem;
    color: var(--text-muted);
}
.disc-author { font-weight: 700; color: var(--steel-frost); font-size: 0.85rem; }
.disc-msg { font-size: 0.9rem; line-height: 1.55; color: var(--text-main); }
.disc-actions { margin-top: 8px; display: flex; gap: 6px; }
.edited-tag { font-size: 0.72rem; color: var(--accent-gold); font-style: italic; }

/* ======== SCROLLBAR ======== */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: var(--steel-darkest); }
::-webkit-scrollbar-thumb { background: var(--steel-mid); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--steel-light); }

code { font-family: monospace; color: var(--steel-pale); font-size: 0.85em; }
</style>
<script>
function togglePW(inputId, btnId) {
    const inp = document.getElementById(inputId);
    const btn = document.getElementById(btnId);
    if (inp.type === 'password') { inp.type = 'text'; btn.textContent = 'Hide'; }
    else { inp.type = 'password'; btn.textContent = 'Show'; }
}
</script>
"""

def render_header():
    name, username, role = get_current_user()
    is_admin = 'admin' in session
    role_cls = ''.join(c for c in role if c.isalnum())
    if is_admin:
        nav = f"""
        <a href="/admin_dashboard">Dashboard</a>
        <a href="/add_shipment">+ New Part</a>
        <a href="/manage_admins">Admins</a>
        <a href="/manage_users">Users</a>
        <a href="/trash">Trash</a>
        <a href="/logout" class="nav-danger">Logout</a>
        """
    elif 'dealer' in session:
        nav = '<a href="/dealer_dashboard">Dashboard</a><a href="/logout" class="nav-danger">Logout</a>'
    else:
        nav = '<a href="/">Login</a>'

    return f"""
    <div class="site-header">
      <div class="header-logo-wrap">
        <img src="{TOYOTA_LOGO}" alt="Toyota">
        <div class="header-brand">
          <span class="brand-main">TKM</span>
          <span class="brand-sub">Toyota Kirloskar Motors</span>
        </div>
      </div>
      <div class="header-center-title">TKM Discussion Portal</div>
      <div class="header-right-wrap">
        <span class="role-tag role-{role_cls}">{role}</span>
        <span class="user-pill">&#128100; {name} &bull; {username}</span>
        <div class="header-nav">{nav}</div>
      </div>
    </div>
    """

def render_login_header():
    return f"""
    <div class="login-header-bar">
      <div class="header-logo-wrap">
        <img src="{TOYOTA_LOGO}" alt="Toyota" style="height:40px;filter:drop-shadow(0 0 6px rgba(200,168,75,0.4))">
        <div class="header-brand">
          <span class="brand-main">TKM</span>
          <span class="brand-sub">Toyota Kirloskar Motors</span>
        </div>
      </div>
      <div class="header-center-title" style="font-size:1.1rem;">TKM Discussion Portal</div>
      <div style="font-size:0.72rem;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;">NTF Discussion System</div>
    </div>
    """

# =========================================================
# AUTH ROUTES
# =========================================================
@app.route('/')
def home():
    html = get_base_style() + render_login_header() + """
    <div class="login-content">
    <div class="login-card">
      <div class="login-logo-area">
        <img src=\"""" + TOYOTA_LOGO + """\" alt="Toyota Logo">
      </div>
      <div class="login-title">User Login</div>
      <div class="login-subtitle">TKM Discussion Portal</div>
      <div class="divider"></div>
      <form method="POST" action="/login">
        <div class="field-group"><label>Username</label>
          <input type="text" name="username" required placeholder="Enter your username"></div>
        <div class="field-group"><label>Password</label>
          <div class="pw-wrap">
            <input type="password" name="password" id="lp" required placeholder="Enter your password">
            <button type="button" class="pw-toggle" id="lpt" onclick="togglePW('lp','lpt')">Show</button>
          </div></div>
        <button type="submit" class="login-btn">Login</button>
      </form>
      <div class="login-links">
        <a href="/register">Register as User</a> &nbsp;&nbsp;|&nbsp;&nbsp; <a href="/admin_login">Admin Login</a>
      </div>
    </div>
    </div>
    """
    return render_template_string(html)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO dealers(name,username,password,department) VALUES(?,?,?,?)",
                (request.form['name'], request.form['username'], request.form['password'], request.form.get('department','General')))
            conn.commit()
        except Exception:
            conn.close()
            return render_template_string(get_base_style() + render_login_header() + """
            <div class="login-content"><div class="login-card">
            <div class="alert alert-danger">Username already exists. <a href="/register" style="color:var(--steel-pale)">Try again</a></div>
            </div></div>""")
        conn.close()
        return redirect('/')
    html = get_base_style() + render_login_header() + """
    <div class="login-content">
    <div class="login-card">
      <div class="login-logo-area"><img src=\"""" + TOYOTA_LOGO + """\" alt="Toyota Logo"></div>
      <div class="login-title">Register</div>
      <div class="login-subtitle">Create your user account</div>
      <div class="divider"></div>
      <form method="POST" action="/register">
        <div class="field-group"><label>Full Name</label>
          <input type="text" name="name" required placeholder="Your full name"></div>
        <div class="field-group"><label>Username</label>
          <input type="text" name="username" required placeholder="Choose a username"></div>
        <div class="field-group"><label>Department</label>
          <select name="department">
            <option value="General">General</option>
            <option value="QAC">QAC</option>
            <option value="QIC">QIC</option>
            <option value="Production">Production</option>
            <option value="Dealer">Dealer</option>
            <option value="Supplier">Supplier</option>
          </select></div>
        <div class="field-group"><label>Password</label>
          <div class="pw-wrap">
            <input type="password" name="password" id="rp" required placeholder="Choose a password">
            <button type="button" class="pw-toggle" id="rpt" onclick="togglePW('rp','rpt')">Show</button>
          </div></div>
        <button type="submit" class="login-btn">Register</button>
      </form>
      <div class="login-links"><a href="/">Back to Login</a></div>
    </div></div>
    """
    return render_template_string(html)

@app.route('/login', methods=['POST'])
def login():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM dealers WHERE username=? AND password=?",
                (request.form['username'], request.form['password']))
    user = cur.fetchone(); conn.close()
    if user:
        session['dealer'] = user['Sl_No']
        session['dealer_name'] = user['name']
        session['dealer_username'] = user['username']
        session['dealer_department'] = user['department']
        return redirect('/dealer_dashboard')
    return render_template_string(get_base_style() + render_login_header() +
        """<div class="login-content"><div class="login-card">
        <div class="alert alert-danger">Invalid credentials. <a href="/" style="color:var(--steel-pale)">Try again</a></div>
        </div></div>""")

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM admins WHERE username=? AND password=?",
                    (request.form['username'], request.form['password']))
        admin = cur.fetchone(); conn.close()
        if admin:
            session['admin'] = admin['Sl_No']
            session['admin_name'] = admin['name']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']
            return redirect('/admin_dashboard')
        return render_template_string(get_base_style() + render_login_header() +
            """<div class="login-content"><div class="login-card">
            <div class="alert alert-danger">Invalid admin credentials. <a href="/admin_login" style="color:var(--steel-pale)">Try again</a></div>
            </div></div>""")
    html = get_base_style() + render_login_header() + """
    <div class="login-content">
    <div class="login-card">
      <div class="login-logo-area"><img src=\"""" + TOYOTA_LOGO + """\" alt="Toyota Logo"></div>
      <div class="login-title">Admin Login</div>
      <div class="login-subtitle">QAC &bull; QIC &bull; Production</div>
      <div class="divider"></div>
      <form method="POST" action="/admin_login">
        <div class="field-group"><label>Username</label>
          <input type="text" name="username" required placeholder="Admin username"></div>
        <div class="field-group"><label>Password</label>
          <div class="pw-wrap">
            <input type="password" name="password" id="ap" required placeholder="Admin password">
            <button type="button" class="pw-toggle" id="apt" onclick="togglePW('ap','apt')">Show</button>
          </div></div>
        <button type="submit" class="login-btn">Login as Admin</button>
      </form>
      <div class="login-links"><a href="/">User Login</a></div>
    </div></div>
    """
    return render_template_string(html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# =========================================================
# DASHBOARD HELPERS
# =========================================================
def build_shipment_table(shipments, is_admin):
    rows = ""
    for s in shipments:
        status_cls = f"status-{s['status']}" if s['status'] else ""
        actions = ""
        if is_admin:
            actions = f"""
            <a href="{url_for('edit_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-warn">Edit</a>
            <a href="{url_for('delete_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-danger"
               onclick="return confirm('Move to trash?')">Delete</a>"""
        rows += f"""
        <tr>
          <td style="color:var(--text-muted)">{s['Sl_No']}</td>
          <td>{s['Date_sent'] or ''}</td>
          <td>{s['Model'] or ''}</td>
          <td><code>{s['Part_Number'] or ''}</code></td>
          <td><strong style="color:var(--steel-frost)">{s['Part_Name'] or ''}</strong></td>
          <td>{s['Supplier_name'] or ''}</td>
          <td style="max-width:160px;white-space:normal;font-size:.8rem">{s['Customer_Concern'] or ''}</td>
          <td>{s['PIC'] or ''}</td>
          <td>{s['category'] or ''}</td>
          <td>{s['Remark'] or ''}</td>
          <td><span class="{status_cls}">{s['status'] or 'Open'}</span></td>
          <td><a href="{url_for('view_discussion', shipment_id=s['Sl_No'])}" class="btn btn-sm btn-success">&#128172; Discuss</a></td>
          {'<td>' + actions + '</td>' if is_admin else ''}
        </tr>"""
    return rows

def build_filter_form(vals, action):
    def sel(name, field, options):
        opts = f'<option value="">All</option>'
        for v in options:
            sel_attr = 'selected' if vals.get(field) == v else ''
            opts += f'<option value="{v}" {sel_attr}>{v}</option>'
        return f'<select name="{field}">{opts}</select>'
    return f"""
    <form method="get" action="{action}" class="form-row">
      <div class="form-group"><label>Search</label>
        <input type="text" name="query" value="{vals.get('query','')}" placeholder="Part Name / Number" style="min-width:160px"></div>
      <div class="form-group"><label>Model</label>
        <input type="text" name="model" value="{vals.get('model','')}" placeholder="Model"></div>
      <div class="form-group"><label>Supplier</label>
        <input type="text" name="supplier" value="{vals.get('supplier','')}" placeholder="Supplier"></div>
      <div class="form-group"><label>Date</label>
        <input type="date" name="date_sent" value="{vals.get('date_sent','')}"></div>
      <div class="form-group"><label>PIC</label>
        <input type="text" name="pic" value="{vals.get('pic','')}" placeholder="PIC"></div>
      <div class="form-group"><label>Status</label>
        {sel('Status','status',['Open','Inprogress','Closed'])}</div>
      <div class="form-group"><label>Remark</label>
        {sel('Remark','remark',['external','NTF','misjudgement'])}</div>
      <div class="form-group"><label>Category</label>
        {sel('Category','category',['electrical','body','chases','engine'])}</div>
      <div class="form-group"><label>&nbsp;</label>
        <button type="submit" class="btn btn-primary">&#128269; Filter</button></div>
    </form>"""

# =========================================================
# DASHBOARDS
# =========================================================
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session: return redirect('/admin_login')
    vals = {k: request.args.get(k,'') for k in ['query','model','supplier','date_sent','pic','status','remark','category']}
    page = int(request.args.get('page',1))
    offset = (page-1)*PER_PAGE
    sql_base = "FROM shipments WHERE is_deleted=0"
    params = []
    if vals['query']:
        sql_base += " AND (Part_Name LIKE ? OR Part_Number LIKE ?)"; params.extend([f"%{vals['query']}%"]*2)
    if vals['model']:   sql_base += " AND Model LIKE ?"; params.append(f"%{vals['model']}%")
    if vals['supplier']:sql_base += " AND Supplier_name LIKE ?"; params.append(f"%{vals['supplier']}%")
    if vals['date_sent']:sql_base += " AND Date_sent=?"; params.append(vals['date_sent'])
    if vals['pic']:     sql_base += " AND PIC LIKE ?"; params.append(f"%{vals['pic']}%")
    if vals['status']:  sql_base += " AND status=?"; params.append(vals['status'])
    if vals['remark']:  sql_base += " AND Remark=?"; params.append(vals['remark'])
    if vals['category']:sql_base += " AND category=?"; params.append(vals['category'])
    conn = get_db(); cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as cnt {sql_base}", params)
    total_items = cur.fetchone()['cnt']
    total_pages = max(1,(total_items+PER_PAGE-1)//PER_PAGE)
    cur.execute(f"SELECT * {sql_base} ORDER BY Sl_No DESC LIMIT ? OFFSET ?", params+[PER_PAGE,offset])
    shipments = cur.fetchall(); conn.close()
    rows = build_shipment_table(shipments, True)
    qs = '&'.join(f"{k}={v}" for k,v in vals.items() if v)
    pagination = "".join([f'<a href="?page={p}&{qs}" class="{"active" if p==page else ""}">{p}</a>' for p in range(1,total_pages+1)])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      <div class="card">{build_filter_form(vals, '/admin_dashboard')}</div>
      <div class="card">
        <h3 style="margin-bottom:12px">&#128230; Parts / Shipments &nbsp;
          <small style="color:var(--text-dim);font-weight:400;font-family:'IBM Plex Sans',sans-serif;font-size:.85rem">{total_items} records</small></h3>
        <div class="table-wrap"><table>
          <thead><tr><th>SL</th><th>Date</th><th>Model</th><th>Part No.</th><th>Part Name</th>
            <th>Supplier</th><th>Concern</th><th>PIC</th><th>Category</th>
            <th>Remark</th><th>Status</th><th>Discussion</th><th>Actions</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>
        <div class="pagination">{pagination}</div>
      </div>
    </div>"""
    return render_template_string(html)

@app.route('/dealer_dashboard')
def dealer_dashboard():
    if 'dealer' not in session: return redirect('/')
    page = int(request.args.get('page',1))
    query = request.args.get('query','')
    status_filter = request.args.get('status','')
    offset = (page-1)*PER_PAGE
    sql_base = "FROM shipments WHERE is_deleted=0"
    params = []
    if query:
        sql_base += " AND (Part_Name LIKE ? OR Part_Number LIKE ?)"; params.extend([f"%{query}%"]*2)
    if status_filter: sql_base += " AND status=?"; params.append(status_filter)
    conn = get_db(); cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as cnt {sql_base}", params)
    total_items = cur.fetchone()['cnt']
    total_pages = max(1,(total_items+PER_PAGE-1)//PER_PAGE)
    cur.execute(f"SELECT * {sql_base} ORDER BY Sl_No DESC LIMIT ? OFFSET ?", params+[PER_PAGE,offset])
    shipments = cur.fetchall(); conn.close()
    rows = build_shipment_table(shipments, False)
    pagination = "".join([f'<a href="?page={p}&query={query}&status={status_filter}" class="{"active" if p==page else ""}">{p}</a>' for p in range(1,total_pages+1)])
    opts = "".join([f'<option value="{v}" {"selected" if status_filter==v else ""}>{v}</option>' for v in ['Open','Inprogress','Closed']])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      <div class="card">
        <form method="get" action="/dealer_dashboard" class="form-row">
          <div class="form-group"><label>Search</label>
            <input type="text" name="query" value="{query}" placeholder="Part Name / Number"></div>
          <div class="form-group"><label>Status</label>
            <select name="status"><option value="">All</option>{opts}</select></div>
          <div class="form-group"><label>&nbsp;</label>
            <button type="submit" class="btn btn-primary">Filter</button></div>
        </form>
      </div>
      <div class="card">
        <h3 style="margin-bottom:12px">&#128230; Available Parts &nbsp;
          <small style="color:var(--text-dim);font-weight:400;font-family:'IBM Plex Sans',sans-serif">{total_items} records</small></h3>
        <div class="table-wrap"><table>
          <thead><tr><th>SL</th><th>Date</th><th>Model</th><th>Part No.</th><th>Part Name</th>
            <th>Supplier</th><th>Concern</th><th>PIC</th><th>Category</th>
            <th>Remark</th><th>Status</th><th>Discussion</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>
        <div class="pagination">{pagination}</div>
      </div>
    </div>"""
    return render_template_string(html)

# =========================================================
# ADD / EDIT SHIPMENT
# =========================================================
def shipment_form(action, data=None, btn="Add Part"):
    d = data or {}
    def v(k): return d.get(k,'') if isinstance(d,dict) else (d[k] if k in d.keys() else '')
    def sel(name, opts, cur):
        o = "".join([f'<option value="{x}" {"selected" if cur==x else ""}>{x if x else "--Select--"}</option>' for x in opts])
        return f'<select name="{name}">{o}</select>'
    return f"""
    <form method="POST" action="{action}">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      <div class="form-group"><label>Part Name *</label>
        <input type="text" name="part_name" value="{v('Part_Name')}" required></div>
      <div class="form-group"><label>Part Number *</label>
        <input type="text" name="part_number" value="{v('Part_Number')}" required></div>
      <div class="form-group"><label>Model</label>
        <input type="text" name="model" value="{v('Model')}"></div>
      <div class="form-group"><label>Supplier Name</label>
        <input type="text" name="supplier" value="{v('Supplier_name')}"></div>
      <div class="form-group"><label>Date Sent</label>
        <input type="date" name="date_sent" value="{v('Date_sent')}"></div>
      <div class="form-group"><label>PIC</label>
        <input type="text" name="pic" value="{v('PIC')}"></div>
      <div class="form-group"><label>Status</label>
        {sel('status',['Open','Inprogress','Closed'], v('status') or 'Open')}</div>
      <div class="form-group"><label>Remark</label>
        {sel('remark',['','external','NTF','misjudgement'], v('Remark'))}</div>
      <div class="form-group"><label>Category</label>
        {sel('category',['','electrical','body','chases','engine'], v('category'))}</div>
    </div>
    <div class="form-group" style="margin-top:12px"><label>Customer Concern</label>
      <textarea name="customer_concern" rows="3" style="width:100%">{v('Customer_Concern')}</textarea></div>
    <br>
    <button type="submit" class="btn btn-primary">{btn}</button>
    &nbsp;<a href="/admin_dashboard" class="btn" style="background:rgba(42,106,191,0.15);color:var(--chrome-2);border:1px solid var(--border-light)">Cancel</a>
    </form>"""

@app.route('/add_shipment', methods=['GET','POST'])
def add_shipment():
    if 'admin' not in session: return redirect('/admin_login')
    if request.method == 'POST':
        name, username, role = get_current_user()
        conn = get_db(); cur = conn.cursor()
        cur.execute("""INSERT INTO shipments
        (Part_Name,Part_Number,Model,Supplier_name,Date_sent,status,Remark,PIC,category,Customer_Concern,created_by,created_by_role,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (request.form['part_name'],request.form['part_number'],request.form['model'],
         request.form['supplier'],request.form['date_sent'],request.form['status'],
         request.form['remark'],request.form['pic'],request.form['category'],
         request.form['customer_concern'],username,role,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()
        return redirect('/admin_dashboard')
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap"><div class="card">
      <h2>&#10133; New Part / Shipment</h2><br>
      {shipment_form('/add_shipment', btn='Add Part')}
    </div></div>"""
    return render_template_string(html)

@app.route('/edit_shipment/<int:slno>', methods=['GET','POST'])
def edit_shipment(slno):
    if 'admin' not in session: return redirect('/admin_login')
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("""UPDATE shipments SET
        Part_Name=?,Part_Number=?,Model=?,Supplier_name=?,Date_sent=?,status=?,Remark=?,PIC=?,category=?,Customer_Concern=?
        WHERE Sl_No=?""",
        (request.form['part_name'],request.form['part_number'],request.form['model'],
         request.form['supplier'],request.form['date_sent'],request.form['status'],
         request.form['remark'],request.form['pic'],request.form['category'],
         request.form['customer_concern'],slno))
        conn.commit(); conn.close()
        return redirect('/admin_dashboard')
    cur.execute("SELECT * FROM shipments WHERE Sl_No=?", (slno,))
    shipment = cur.fetchone(); conn.close()
    s = dict(shipment)
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap"><div class="card">
      <h2>&#9999;&#65039; Edit Shipment #{slno}</h2><br>
      {shipment_form(f'/edit_shipment/{slno}', s, btn='Update Part')}
    </div></div>"""
    return render_template_string(html)

# =========================================================
# DELETE / TRASH
# =========================================================
@app.route('/delete_shipment/<int:slno>')
def delete_shipment(slno):
    if 'admin' not in session: return redirect('/admin_login')
    conn = get_db(); conn.execute("UPDATE shipments SET is_deleted=1 WHERE Sl_No=?",(slno,)); conn.commit(); conn.close()
    return redirect('/admin_dashboard')

@app.route('/trash')
def trash():
    if 'admin' not in session: return redirect('/admin_login')
    page = int(request.args.get('page',1)); offset=(page-1)*PER_PAGE
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM shipments WHERE is_deleted=1")
    total_items=cur.fetchone()['cnt']; total_pages=max(1,(total_items+PER_PAGE-1)//PER_PAGE)
    cur.execute("SELECT * FROM shipments WHERE is_deleted=1 LIMIT ? OFFSET ?",(PER_PAGE,offset))
    shipments=cur.fetchall(); conn.close()
    rows=""
    for s in shipments:
        rows += f"""<tr>
          <td>{s['Sl_No']}</td><td>{s['Date_sent'] or ''}</td><td>{s['Model'] or ''}</td>
          <td>{s['Part_Number'] or ''}</td><td>{s['Part_Name'] or ''}</td>
          <td>{s['Supplier_name'] or ''}</td><td>{s['status'] or ''}</td>
          <td>
            <a href="{url_for('restore_shipment',slno=s['Sl_No'])}" class="btn btn-sm btn-success">Restore</a>
            <a href="{url_for('permanent_delete_shipment',slno=s['Sl_No'])}" class="btn btn-sm btn-danger"
               onclick="return confirm('Permanently delete?')">Delete Forever</a>
          </td></tr>"""
    pagination="".join([f'<a href="?page={p}" class="{"active" if p==page else ""}">{p}</a>' for p in range(1,total_pages+1)])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap"><div class="card">
      <h2>&#128465;&#65039; Trash ({total_items} items)</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>SL</th><th>Date</th><th>Model</th><th>Part No.</th><th>Part Name</th><th>Supplier</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>{rows}</tbody>
      </table></div>
      <div class="pagination">{pagination}</div>
    </div></div>"""
    return render_template_string(html)

@app.route('/restore_shipment/<int:slno>')
def restore_shipment(slno):
    if 'admin' not in session: return redirect('/admin_login')
    conn=get_db(); conn.execute("UPDATE shipments SET is_deleted=0 WHERE Sl_No=?",(slno,)); conn.commit(); conn.close()
    return redirect('/trash')

@app.route('/permanent_delete_shipment/<int:slno>')
def permanent_delete_shipment(slno):
    if 'admin' not in session: return redirect('/admin_login')
    conn=get_db(); conn.execute("DELETE FROM shipments WHERE Sl_No=?",(slno,)); conn.commit(); conn.close()
    return redirect('/trash')

# =========================================================
# DISCUSSION
# =========================================================
@app.route('/discussion/<int:shipment_id>', methods=['GET','POST'])
def view_discussion(shipment_id):
    if 'admin' not in session and 'dealer' not in session: return redirect('/')
    name, username, role = get_current_user()
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action','post')
        if action == 'post':
            cur.execute("""INSERT INTO Discussion
            (shipment_id,pi_number,message,dept,created_at,author_name,author_username,author_role)
            VALUES(?,?,?,?,?,?,?,?)""",
            (shipment_id, request.form.get('pi_number',''), request.form.get('message',''),
             request.form.get('dept', role), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             name, username, role))
            conn.commit()
        elif action == 'edit':
            disc_id = int(request.form.get('disc_id',0))
            cur.execute("SELECT * FROM Discussion WHERE Sl_No=?", (disc_id,))
            disc = cur.fetchone()
            if disc and (disc['author_username']==username or 'admin' in session):
                cur.execute("UPDATE Discussion SET message=?,edited=1,edited_at=?,edited_by=? WHERE Sl_No=?",
                    (request.form.get('message',''), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     f"{name} ({username})", disc_id))
                conn.commit()
        elif action == 'delete':
            disc_id = int(request.form.get('disc_id',0))
            cur.execute("SELECT * FROM Discussion WHERE Sl_No=?", (disc_id,))
            disc = cur.fetchone()
            if disc and (disc['author_username']==username or 'admin' in session):
                cur.execute("UPDATE Discussion SET is_deleted=1,edited_by=?,edited_at=? WHERE Sl_No=?",
                    (f"Deleted by {name} ({username})", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disc_id))
                conn.commit()
    cur.execute("SELECT * FROM shipments WHERE Sl_No=?", (shipment_id,))
    shipment = cur.fetchone()
    cur.execute("SELECT * FROM Discussion WHERE shipment_id=? ORDER BY Sl_No ASC", (shipment_id,))
    discussions = cur.fetchall(); conn.close()
    back_link = '/admin_dashboard' if 'admin' in session else '/dealer_dashboard'
    disc_html = ""
    for d in discussions:
        is_mine = (d['author_username']==username)
        can_edit = is_mine or 'admin' in session
        deleted = d['is_deleted']==1
        role_cls = ''.join(c for c in (d['author_role'] or 'user') if c.isalnum())
        edited_tag = f'<span class="edited-tag">&#9998; edited {d["edited_at"] or ""} by {d["edited_by"] or ""}</span>' if d['edited'] and not deleted else ""
        deleted_label = f'<span style="color:#f07070;font-size:.78rem">&#128465; {d["edited_by"] or "Deleted"} &bull; {d["edited_at"] or ""}</span>' if deleted else ""
        msg_text = "<em style='color:var(--text-dim)'>[This message was deleted]</em>" if deleted else f'<div class="disc-msg">{d["message"]}</div>'
        edit_form = ""
        if can_edit and not deleted:
            edit_form = f"""
            <div id="ef-{d['Sl_No']}" style="display:none;margin-top:8px">
              <form method="POST">
                <input type="hidden" name="action" value="edit">
                <input type="hidden" name="disc_id" value="{d['Sl_No']}">
                <textarea name="message" rows="2" style="width:100%">{d['message']}</textarea><br>
                <button type="submit" class="btn btn-sm btn-primary" style="margin-top:4px">Save</button>
                <button type="button" class="btn btn-sm" style="background:rgba(42,106,191,0.15);color:var(--chrome-2);border:1px solid var(--border-light)"
                  onclick="document.getElementById('ef-{d["Sl_No"]}').style.display='none'">Cancel</button>
              </form>
            </div>"""
            actions_html = f"""
            <div class="disc-actions">
              <button type="button" class="btn btn-sm btn-warn"
                onclick="document.getElementById('ef-{d["Sl_No"]}').style.display='block'">Edit</button>
              <form method="POST" style="display:inline">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="disc_id" value="{d['Sl_No']}">
                <button type="submit" class="btn btn-sm btn-danger"
                  onclick="return confirm('Delete this message?')">Delete</button>
              </form>
            </div>"""
        else:
            actions_html = ""
        disc_html += f"""
        <div class="disc-card {"deleted" if deleted else ""}">
          <div class="disc-meta">
            <span class="disc-author">{d['author_name'] or 'Unknown'}</span>
            <span class="role-tag role-{role_cls}">{d['author_role'] or 'User'}</span>
            <span style="color:var(--text-dim)">@{d['author_username'] or ''}</span>
            {'<span>&bull;</span><span>' + (d['pi_number'] or '') + '</span>' if d['pi_number'] else ''}
            {'<span>&bull;</span><span>' + (d['dept'] or '') + '</span>' if d['dept'] else ''}
            <span>&bull;</span><span>{d['created_at'] or ''}</span>
            {edited_tag}
          </div>
          {msg_text}
          {deleted_label}
          {actions_html}
          {edit_form}
        </div>"""
    if not disc_html:
        disc_html = "<p style='color:var(--text-dim);text-align:center;padding:24px'>No messages yet. Be the first to post!</p>"
    part_info = ""
    if shipment:
        part_info = f"""<div class="alert alert-info" style="margin-bottom:14px">
          <strong>Part:</strong> {shipment['Part_Name']} &nbsp;|&nbsp;
          <strong>No.:</strong> {shipment['Part_Number']} &nbsp;|&nbsp;
          <strong>Model:</strong> {shipment['Model']} &nbsp;|&nbsp;
          <strong>Status:</strong> <span class="status-{shipment['status']}">{shipment['status']}</span>
        </div>"""
    msg_count = len(discussions)
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      <div style="margin-bottom:12px">
        <a href="{back_link}" class="btn btn-primary">&#8592; Back to Dashboard</a>
      </div>
      {part_info}
      <div class="card">
        <h2>&#128172; Post a Message</h2>
        <form method="POST" style="margin-top:12px">
          <input type="hidden" name="action" value="post">
          <div class="form-row">
            <div class="form-group"><label>PI Number</label>
              <input type="text" name="pi_number" placeholder="PI Number"></div>
            <div class="form-group"><label>Department</label>
              <input type="text" name="dept" value="{role}" placeholder="Department"></div>
          </div>
          <div class="form-group" style="margin-top:10px"><label>Message</label>
            <textarea name="message" rows="3" style="width:100%" required placeholder="Type your message..."></textarea></div>
          <button type="submit" class="btn btn-primary" style="margin-top:10px">&#128228; Post Message</button>
        </form>
      </div>
      <div class="card">
        <h3>Messages ({msg_count})</h3>
        <div style="max-height:550px;overflow-y:auto;padding-right:4px;margin-top:10px">{disc_html}</div>
      </div>
    </div>"""
    return render_template_string(html)

# =========================================================
# MANAGE ADMINS
# =========================================================
@app.route('/manage_admins', methods=['GET','POST'])
def manage_admins():
    if 'admin' not in session: return redirect('/admin_login')
    conn=get_db(); cur=conn.cursor(); msg=""
    if request.method=='POST':
        action=request.form.get('action')
        if action=='add':
            try:
                cur.execute("INSERT INTO admins(name,username,password,role) VALUES(?,?,?,?)",
                    (request.form['name'],request.form['username'],request.form['password'],request.form['role']))
                conn.commit(); msg="add_ok"
            except: msg="add_err"
        elif action=='delete':
            aid=int(request.form.get('admin_id',0))
            if aid!=session['admin']:
                cur.execute("DELETE FROM admins WHERE Sl_No=?",(aid,)); conn.commit(); msg="del_ok"
            else: msg="del_self"
        elif action=='change_password':
            cur.execute("UPDATE admins SET password=? WHERE Sl_No=?",(request.form['new_password'],int(request.form.get('admin_id',0))))
            conn.commit(); msg="pw_ok"
    cur.execute("SELECT * FROM admins ORDER BY Sl_No")
    admins=cur.fetchall(); conn.close()
    alert_map = {
        'add_ok': ('success','Admin added successfully.'),
        'add_err': ('danger','Username already exists.'),
        'del_ok': ('success','Admin deleted.'),
        'del_self': ('danger','Cannot delete your own account.'),
        'pw_ok': ('success','Password updated.'),
    }
    alert_html = ""
    if msg in alert_map:
        cls, text = alert_map[msg]
        alert_html = f'<div class="alert alert-{cls}">{text}</div>'
    rows=""
    for a in admins:
        role_cls=''.join(c for c in a['role'] if c.isalnum())
        you=" <small style='color:var(--accent-gold)'>(you)</small>" if a['Sl_No']==session['admin'] else ""
        rows += f"""<tr>
          <td style="color:var(--text-muted)">{a['Sl_No']}</td>
          <td>{a['name']}{you}</td>
          <td><code>{a['username']}</code></td>
          <td><span class="role-tag role-{role_cls}">{a['role']}</span></td>
          <td>
            <form method="POST" style="display:inline">
              <input type="hidden" name="action" value="change_password">
              <input type="hidden" name="admin_id" value="{a['Sl_No']}">
              <input type="password" name="new_password" placeholder="New password" style="width:120px">
              <button type="submit" class="btn btn-sm btn-warn">Update PW</button>
            </form>
            {"" if a['Sl_No']==session['admin'] else f"""
            <form method="POST" style="display:inline">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="admin_id" value="{a['Sl_No']}">
              <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Delete admin?')">Delete</button>
            </form>"""}
          </td></tr>"""
    role_opts="".join([f'<option value="{r}">{r}</option>' for r in ['QACAdmin','QICAdmin','ProductionAdmin']])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      {alert_html}
      <div class="card">
        <h2>&#10133; Add New Admin</h2><br>
        <form method="POST" class="form-row">
          <input type="hidden" name="action" value="add">
          <div class="form-group"><label>Full Name</label>
            <input type="text" name="name" required placeholder="Admin full name"></div>
          <div class="form-group"><label>Username</label>
            <input type="text" name="username" required placeholder="Username"></div>
          <div class="form-group"><label>Password</label>
            <input type="password" name="password" required placeholder="Password"></div>
          <div class="form-group"><label>Role</label>
            <select name="role">{role_opts}</select></div>
          <div class="form-group"><label>&nbsp;</label>
            <button type="submit" class="btn btn-primary">Add Admin</button></div>
        </form>
      </div>
      <div class="card">
        <h2>&#128101; All Admins</h2>
        <div class="table-wrap"><table>
          <thead><tr><th>ID</th><th>Name</th><th>Username</th><th>Role</th><th>Actions</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>
      </div>
    </div>"""
    return render_template_string(html)

# =========================================================
# MANAGE USERS
# =========================================================
@app.route('/manage_users', methods=['GET','POST'])
def manage_users():
    if 'admin' not in session: return redirect('/admin_login')
    conn=get_db(); cur=conn.cursor(); msg=""
    if request.method=='POST':
        action=request.form.get('action')
        if action=='delete':
            cur.execute("DELETE FROM dealers WHERE Sl_No=?",(int(request.form.get('user_id',0)),)); conn.commit(); msg="del_ok"
        elif action=='change_password':
            cur.execute("UPDATE dealers SET password=? WHERE Sl_No=?",(request.form['new_password'],int(request.form.get('user_id',0)))); conn.commit(); msg="pw_ok"
    cur.execute("SELECT * FROM dealers ORDER BY Sl_No")
    users=cur.fetchall(); conn.close()
    alert_html=""
    if msg=='del_ok': alert_html='<div class="alert alert-success">User deleted.</div>'
    elif msg=='pw_ok': alert_html='<div class="alert alert-success">Password updated.</div>'
    rows=""
    for u in users:
        rows += f"""<tr>
          <td style="color:var(--text-muted)">{u['Sl_No']}</td>
          <td>{u['name']}</td><td><code>{u['username']}</code></td><td>{u['department']}</td>
          <td>
            <form method="POST" style="display:inline">
              <input type="hidden" name="action" value="change_password">
              <input type="hidden" name="user_id" value="{u['Sl_No']}">
              <input type="password" name="new_password" placeholder="New password" style="width:120px">
              <button type="submit" class="btn btn-sm btn-warn">Update PW</button>
            </form>
            <form method="POST" style="display:inline">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="user_id" value="{u['Sl_No']}">
              <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Delete user?')">Delete</button>
            </form>
          </td></tr>"""
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      {alert_html}
      <div class="card">
        <h2>&#128100; All Users ({len(users)})</h2>
        <div class="table-wrap"><table>
          <thead><tr><th>ID</th><th>Name</th><th>Username</th><th>Department</th><th>Actions</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>
      </div>
    </div>"""
    return render_template_string(html)

# =========================================================
# PUBLIC ACCESS
# =========================================================
if __name__ == "__main__":
    import socket
    init_db()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    port = 5000
    print("=" * 60)
    print("  TKM Discussion Portal — Toyota Kirloskar Motors")
    print("=" * 60)
    print(f"  Local:   http://127.0.0.1:{port}")
    print(f"  Network (LAN): http://{local_ip}:{port}  <- Share on WiFi")
    print()
    print("  Default Admin Credentials:")
    print("  Role             | Username  | Password")
    print("  QACAdmin         | qacadmin  | qac123")
    print("  QICAdmin         | qicadmin  | qic123")
    print("  ProductionAdmin  | prodadmin | prod123")
    print()
    print("  For INTERNET access run:")
    print("  pip install pyngrok")
    print("  python -c \"from pyngrok import ngrok; print(ngrok.connect(5000))\"")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
