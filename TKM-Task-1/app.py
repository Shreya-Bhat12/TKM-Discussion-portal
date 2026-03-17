from flask import Flask, request, redirect, session, render_template_string, send_file, url_for
import sqlite3
from datetime import datetime
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = "tkm_ntf_secret_2025"

DB_FILE = "model.db"
PER_PAGE = 10

# Toyota logo embedded as base64 - no external file needed
TOYOTA_LOGO = "data:image/png;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAFsAcMDASIAAhEBAxEB/8QAHQABAAIDAQEBAQAAAAAAAAAAAAYHBAUIAwIBCf/EAE4QAAEEAQIDBAcEBQgIBQQDAAEAAgMEBQYRBxIhEzFBUQgUImFxgZEyQqGxFSNSYsEWJDM0Q4KS0QkXU3KTosLhVWODsvAlVHPxNURk/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAXEQEBAQEAAAAAAAAAAAAAAAAAEQEh/9oADAMBAAIRAxEAPwDstERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBF5WrNerEZrU8UEY73yPDWj5lQLVXGXh9p57oJ87HbsjoIabXTFx8t2Aj8UFhIqJscc9QZeTstGcPMpbJ6CS43s2H39Cvnf0g9Sg7T4zTteQdWtY17mj3O23QXtJJHE3mke1jfNx2C1WT1Pp7GM57+ZowNHi6YfwVOf6ktYZZp/lJxKzFhj/ALcMdh4Z9N9lsMV6NuhK0nbXRavSnq50rydz9UEoyPGnhpTJb/KipYeO9kO7iFpLnpD8P4dxCMvad3Dsam4J/wASkON4RcPqDQItOU3beLowVv6ekdMUgBWwtGPbyhb/AJIKrm9IWpJ1xujs1aG24Lm8nX6FY/8Ar51JI4CrwvyMoI7za5f+hXW2njoRtHTrtHujAXy/1dv2YYx8GhWCkzxh4kWJi6rwzljiPc19ncj58q+pOKPFiWMiDh9DE7wc+wSPpyq45Joh4MH0WNLYhHeWJBUcPEvi7E7msaHqyt27mbhP/FSTDam4ea9yDmVbMM2Tp9dLhvw/eXFiw8Y7gY8f0VYxarqRrCaHMWqsv7N5A8QD4LhWstWamYq1qOO7Ua8TQeJGFz3D6nuQXcioTh/x8OoMRf/AEzWqQ6is7yvkY2ZvJNvuQ8eI/aq5n4l8Y82+WS/qS22Fo3dHVDYQPJrRsg6ORVF6PmoLuqeHNWtlrT7eSxT3Y6w9+w9eVzRt7gR8FbqAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiIC1+fy8OBwt3KzDlZWhLwPFx8Pktp0CiHpK6kfhNE+qNkc2a+8Vjl85D/AFn+lBWzGS5Cts9ZIme5rfHv+ikfA3TbZ4p8nNGC2Bhjjd5cwOf/AF2VRabxjr2RrVS3eR3UR+JXQmnqEWMx8FSOPkDAAAPFWyPVERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBF5WrNerEZrU8UEY73yPDWj5lQLVXGXh9p57oJ87HbsjoIabXTFx8t2Aj8UFhIqJscc9QZeTstGcPMpbJ6CS43s2H39Cvnf0g9Sg7T4zTteQdWtY17mj3O23QXtJJHE3mke1jfNx2C1WT1Pp7GM57+ZowNHi6YfwVOf6ktYZZp/lJxKzFhj/ALcMdh4Z9N9lsMV6NuhK0nbXRavSnq50rydz9UEoyPGnhpTJb/KipYeO9kO7iFpLnpD8P4dxCMvad3Dsam4J/wASkON4RcPqDQItOU3beLowVv6ekdMUgBWwtGPbyhb/AJIKrm9IWpJ1xujs1aG24Lm8nX6FY/8Ar51JI4CrwvyMoI7za5f+hXW2njoRtHTrtHujAXy/1dv2YYx8GhWCkzxh4kWJi6rwzljiPc19ncj58q+pOKPFiWMiDh9DE7wc+wSPpyq45Joh4MH0WNLYhHeWJBUcPEvi7E7msaHqyt27mbhP/FSTDam4ea9yDmVbMM2Tp9dLhvw/eXFiw8Y7gY8f0VYxarqRrCaHMWqsv7N5A8QD4LhWstWamYq1qOO7Ua8TQeJGFz3D6nuQXcioTh/x8OoMRf/AEzWqQ6is7yvkY2ZvJNvuQ8eI/aq5n4l8Y82+WS/qS22Fo3dHVDYQPJrRsg6ORVF6PmoLuqeHNWtlrT7eSxT3Y6w9+w9eVzRt7gR8FbqAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiIC1+fy8OBwt3KzDlZWhLwPFx8Pktp0CiHpK6kfhNE+qNkc2a+8Vjl85D/AFn+lBWzGS5Cts9ZIme5rfHv+ikfA3TbZ4p8nNGC2Bhjjd5cwOf/AF2VRabxjr2RrVS3eR3UR+JXQmnqEWMx8FSOPkDAAAPFWyPVERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQH/2Q=="

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
        return session.get('admin_name', 'Admin'), session.get('admin_username', 'admin'), session.get('admin_role', 'Admin')
    elif 'dealer' in session:
        return session.get('dealer_name', 'User'), session.get('dealer_username', 'user'), session.get('dealer_department', 'General')
    return 'Unknown', 'unknown', 'Unknown'

# =========================================================
# GLOBAL STYLE — metallic blue theme
# =========================================================
def get_base_style():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
:root {
    --steel-darkest: #162d50;
    --steel-darker:  #2d518a;
    --steel-dark:    #2454b4;
    --steel-mid:     #357de9;
    --steel-base:    #2a6abf;
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
    --bg-page:       #2c4a83;
    --bg-card:       #0f3986;
    --bg-card2:      #28386e;
    --border-light:  rgba(90,140,200,0.25);
    --border-glow:   rgba(46, 136, 247, 0.5);
    --text-main:     #f5f7fa;
    --text-muted:    #a5c7eb;
    --text-dim:      #a5caf0;
    --shadow-blue:   0 4px 20px rgba(6, 27, 58, 0.4);
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

/* ======== WHATSAPP-STYLE DISCUSSION ======== */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px 4px;
    max-height: 600px;
    overflow-y: auto;
}

.chat-bubble-wrap {
    display: flex;
    flex-direction: column;
    max-width: 68%;
}
.chat-bubble-wrap.left  { align-self: flex-start; align-items: flex-start; }
.chat-bubble-wrap.right { align-self: flex-end;   align-items: flex-end; }

.chat-bubble {
    position: relative;
    padding: 10px 14px 8px 14px;
    border-radius: 14px;
    font-size: 0.88rem;
    line-height: 1.5;
    word-break: break-word;
    box-shadow: 0 3px 12px rgba(0,0,0,0.35);
}

/* Admin / left bubble — steel-blue metallic */
.chat-bubble.left {
    background: linear-gradient(145deg, #0e2a50, #1a4080);
    border: 1px solid rgba(58,133,224,0.35);
    border-top-left-radius: 4px;
    color: var(--text-main);
}
.chat-bubble.left::before {
    content: '';
    position: absolute;
    left: -8px; top: 12px;
    border-width: 6px 9px 6px 0;
    border-style: solid;
    border-color: transparent #1a4080 transparent transparent;
}

/* User / right bubble — teal-gold metallic */
.chat-bubble.right {
    background: linear-gradient(145deg, #0a3a2a, #155a3a);
    border: 1px solid rgba(26,138,90,0.4);
    border-top-right-radius: 4px;
    color: #d0ffe8;
}
.chat-bubble.right::before {
    content: '';
    position: absolute;
    right: -8px; top: 12px;
    border-width: 6px 0 6px 9px;
    border-style: solid;
    border-color: transparent transparent transparent #155a3a;
}

/* Deleted bubble */
.chat-bubble.deleted-bubble {
    background: rgba(10,14,20,0.5) !important;
    border: 1px dashed rgba(120,120,140,0.3) !important;
    color: var(--text-dim) !important;
    font-style: italic;
}
.chat-bubble.deleted-bubble::before { display: none; }

.bubble-header {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 5px;
    flex-wrap: wrap;
}
.bubble-author {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: 0.3px;
}
.left  .bubble-author { color: var(--steel-pale); }
.right .bubble-author { color: #5af0a0; }

.bubble-pi {
    font-size: 0.72rem;
    background: rgba(200,168,75,0.18);
    border: 1px solid rgba(200,168,75,0.35);
    color: var(--accent-gold);
    padding: 1px 6px;
    border-radius: 3px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.bubble-time {
    font-size: 0.69rem;
    color: rgba(180,200,230,0.55);
    margin-top: 5px;
    text-align: right;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 5px;
}
.left .bubble-time { justify-content: flex-start; }

.edited-tag {
    font-size: 0.69rem;
    color: var(--accent-gold);
    font-style: italic;
}

.bubble-actions {
    display: flex;
    gap: 5px;
    margin-top: 5px;
}

.bubble-edit-form {
    margin-top: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 8px;
}

/* Metallic sheen on bubbles */
.chat-bubble::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 40%;
    border-radius: inherit;
    background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, transparent 100%);
    pointer-events: none;
}

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO dealers(name,username,password,department) VALUES(?,?,?,?)",
                (request.form['name'], request.form['username'], request.form['password'], request.form.get('department', 'General')))
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
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM dealers WHERE username=? AND password=?",
                (request.form['username'], request.form['password']))
    user = cur.fetchone()
    conn.close()
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

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admins WHERE username=? AND password=?",
                    (request.form['username'], request.form['password']))
        admin = cur.fetchone()
        conn.close()
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

@app.route('/export_discussion/<int:shipment_id>')
def export_discussion(shipment_id):
    if 'admin' not in session and 'dealer' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT pi_number, message, dept, created_at,
               author_name, author_username, author_role,
               edited, edited_at, edited_by
        FROM Discussion
        WHERE shipment_id=? AND is_deleted=0
        ORDER BY Sl_No ASC
    """, (shipment_id,))
    rows = cur.fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output,
                     download_name=f"discussion_{shipment_id}.xlsx",
                     as_attachment=True)

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
        if is_admin:
            actions = f"""
            <a href="{url_for('edit_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-warn">Edit</a>
            <a href="{url_for('delete_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-danger"
               onclick="return confirm('Move to trash?')">Delete</a>"""
        else:
            actions = f"""
            <a href="{url_for('edit_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-warn">Edit</a>"""
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
          <td>{actions}</td>
        </tr>"""
    return rows

def build_filter_form(vals, action):
    def sel(name, field, options):
        opts = '<option value="">All</option>'
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
      <div class="form-group"><label>PI Number</label>
        <input type="text" name="pic" value="{vals.get('pic','')}" placeholder="PI Number"></div>
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
    if 'admin' not in session:
        return redirect('/admin_login')
    vals = {k: request.args.get(k, '') for k in ['query', 'model', 'supplier', 'date_sent', 'pic', 'status', 'remark', 'category']}
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PER_PAGE
    sql_base = "FROM shipments WHERE is_deleted=0"
    params = []
    if vals['query']:
        sql_base += " AND (Part_Name LIKE ? OR Part_Number LIKE ?)"; params.extend([f"%{vals['query']}%"] * 2)
    if vals['model']:
        sql_base += " AND Model LIKE ?"; params.append(f"%{vals['model']}%")
    if vals['supplier']:
        sql_base += " AND Supplier_name LIKE ?"; params.append(f"%{vals['supplier']}%")
    if vals['date_sent']:
        sql_base += " AND Date_sent=?"; params.append(vals['date_sent'])
    if vals['pic']:
        sql_base += " AND PIC LIKE ?"; params.append(f"%{vals['pic']}%")
    if vals['status']:
        sql_base += " AND status=?"; params.append(vals['status'])
    if vals['remark']:
        sql_base += " AND Remark=?"; params.append(vals['remark'])
    if vals['category']:
        sql_base += " AND category=?"; params.append(vals['category'])
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as cnt {sql_base}", params)
    total_items = cur.fetchone()['cnt']
    total_pages = max(1, (total_items + PER_PAGE - 1) // PER_PAGE)
    cur.execute(f"SELECT * {sql_base} ORDER BY Sl_No DESC LIMIT ? OFFSET ?", params + [PER_PAGE, offset])
    shipments = cur.fetchall()
    conn.close()
    rows = build_shipment_table(shipments, True)
    qs = '&'.join(f"{k}={v}" for k, v in vals.items() if v)
    pagination = "".join([f'<a href="?page={p}&{qs}" class="{"active" if p == page else ""}">{p}</a>' for p in range(1, total_pages + 1)])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      <div class="card">{build_filter_form(vals, '/admin_dashboard')}</div>
      <div class="card">
        <h3 style="margin-bottom:12px">&#128230; Parts / Shipments &nbsp;
          <small style="color:var(--text-dim);font-weight:400;font-family:'IBM Plex Sans',sans-serif;font-size:.85rem">{total_items} records</small></h3>
        <div class="table-wrap"><table>
          <thead><tr><th>SL</th><th>Date</th><th>Model</th><th>Part No.</th><th>Part Name</th>
            <th>Supplier</th><th>Concern</th><th>PI Number</th><th>Category</th>
            <th>Remark</th><th>Status</th><th>Discussion</th><th>Actions</th></tr></thead>
          <tbody>{rows}</tbody>
        </table></div>
        <div class="pagination">{pagination}</div>
      </div>
    </div>"""
    return render_template_string(html)

@app.route('/dealer_dashboard')
def dealer_dashboard():
    if 'dealer' not in session:
        return redirect('/')
    vals = {k: request.args.get(k, '') for k in ['query', 'model', 'supplier', 'date_sent', 'pic', 'status', 'remark', 'category']}
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PER_PAGE
    sql_base = "FROM shipments WHERE is_deleted=0"
    params = []
    if vals['query']:
        sql_base += " AND (Part_Name LIKE ? OR Part_Number LIKE ?)"; params.extend([f"%{vals['query']}%"] * 2)
    if vals['model']:
        sql_base += " AND Model LIKE ?"; params.append(f"%{vals['model']}%")
    if vals['supplier']:
        sql_base += " AND Supplier_name LIKE ?"; params.append(f"%{vals['supplier']}%")
    if vals['date_sent']:
        sql_base += " AND Date_sent=?"; params.append(vals['date_sent'])
    if vals['pic']:
        sql_base += " AND PIC LIKE ?"; params.append(f"%{vals['pic']}%")
    if vals['status']:
        sql_base += " AND status=?"; params.append(vals['status'])
    if vals['remark']:
        sql_base += " AND Remark=?"; params.append(vals['remark'])
    if vals['category']:
        sql_base += " AND category=?"; params.append(vals['category'])
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as cnt {sql_base}", params)
    total_items = cur.fetchone()['cnt']
    total_pages = max(1, (total_items + PER_PAGE - 1) // PER_PAGE)
    cur.execute(f"SELECT * {sql_base} ORDER BY Sl_No DESC LIMIT ? OFFSET ?", params + [PER_PAGE, offset])
    shipments = cur.fetchall()
    conn.close()
    rows = build_shipment_table(shipments, False)
    qs = '&'.join(f"{k}={v}" for k, v in vals.items() if v)
    pagination = "".join([f'<a href="?page={p}&{qs}" class="{"active" if p == page else ""}">{p}</a>' for p in range(1, total_pages + 1)])
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap">
      <div class="card">{build_filter_form(vals, '/dealer_dashboard')}</div>
      <div class="card">
        <h3 style="margin-bottom:12px">&#128230; Available Parts &nbsp;
          <small style="color:var(--text-dim);font-weight:400;font-family:'IBM Plex Sans',sans-serif">{total_items} records</small></h3>
        <div class="table-wrap"><table>
          <thead><tr><th>SL</th><th>Date</th><th>Model</th><th>Part No.</th><th>Part Name</th>
            <th>Supplier</th><th>Concern</th><th>PI Number</th><th>Category</th>
            <th>Remark</th><th>Status</th><th>Discussion</th><th>Actions</th></tr></thead>
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
    def v(k):
        return d.get(k, '') if isinstance(d, dict) else (d[k] if k in d.keys() else '')
    def sel(name, opts, cur):
        o = "".join([f'<option value="{x}" {"selected" if cur == x else ""}>{x if x else "--Select--"}</option>' for x in opts])
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
      <div class="form-group"><label>PI Number</label>
        <input type="text" name="pic" value="{v('PIC')}"></div>
      <div class="form-group"><label>Status</label>
        {sel('status', ['Open', 'Inprogress', 'Closed'], v('status') or 'Open')}</div>
      <div class="form-group"><label>Remark</label>
        {sel('remark', ['', 'external', 'NTF', 'misjudgement'], v('Remark'))}</div>
      <div class="form-group"><label>Category</label>
        {sel('category', ['', 'electrical', 'body', 'chases', 'engine'], v('category'))}</div>
    </div>
    <div class="form-group" style="margin-top:12px"><label>Customer Concern</label>
      <textarea name="customer_concern" rows="3" style="width:100%">{v('Customer_Concern')}</textarea></div>
    <br>
    <button type="submit" class="btn btn-primary">{btn}</button>
    &nbsp;<a href="/admin_dashboard" class="btn" style="background:rgba(42,106,191,0.15);color:var(--chrome-2);border:1px solid var(--border-light)">Cancel</a>
    </form>"""

@app.route('/add_shipment', methods=['GET', 'POST'])
def add_shipment():
    if 'admin' not in session:
        return redirect('/admin_login')
    if request.method == 'POST':
        name, username, role = get_current_user()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO shipments
        (Part_Name,Part_Number,Model,Supplier_name,Date_sent,status,Remark,PIC,category,Customer_Concern,created_by,created_by_role,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (request.form['part_name'], request.form['part_number'], request.form['model'],
         request.form['supplier'], request.form['date_sent'], request.form['status'],
         request.form['remark'], request.form['pic'], request.form['category'],
         request.form['customer_concern'], username, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return redirect('/admin_dashboard')
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap"><div class="card">
      <h2>&#10133; New Part / Shipment</h2><br>
      {shipment_form('/add_shipment', btn='Add Part')}
    </div></div>"""
    return render_template_string(html)

@app.route('/edit_shipment/<int:slno>', methods=['GET', 'POST'])
def edit_shipment(slno):
    if 'admin' not in session and 'dealer' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("""UPDATE shipments SET
        Part_Name=?,Part_Number=?,Model=?,Supplier_name=?,Date_sent=?,status=?,Remark=?,PIC=?,category=?,Customer_Concern=?
        WHERE Sl_No=?""",
        (request.form['part_name'], request.form['part_number'], request.form['model'],
         request.form['supplier'], request.form['date_sent'], request.form['status'],
         request.form['remark'], request.form['pic'], request.form['category'],
         request.form['customer_concern'], slno))
        conn.commit()
        conn.close()
        if 'admin' in session:
            return redirect('/admin_dashboard')
        return redirect('/dealer_dashboard')
    cur.execute("SELECT * FROM shipments WHERE Sl_No=?", (slno,))
    shipment = cur.fetchone()
    conn.close()
    s = dict(shipment)
    back_link = '/admin_dashboard' if 'admin' in session else '/dealer_dashboard'
    html = get_base_style() + render_header() + f"""
    <div class="page-wrap"><div class="card">
      <h2>&#9999;&#65039; Edit Shipment #{slno}</h2><br>
      {shipment_form(f'/edit_shipment/{slno}', s, btn='Update Part')}
      <br><a href="{back_link}" class="btn" style="background:rgba(42,106,191,0.15);color:var(--chrome-2);border:1px solid var(--border-light)">&#8592; Back</a>
    </div></div>"""
    return render_template_string(html)

# =========================================================
# DELETE / TRASH
# =========================================================
@app.route('/delete_shipment/<int:slno>')
def delete_shipment(slno):
    if 'admin' not in session:
        return redirect('/admin_login')
    conn = get_db()
    conn.execute("UPDATE shipments SET is_deleted=1 WHERE Sl_No=?", (slno,))
    conn.commit()
    conn.close()
    return redirect('/admin_dashboard')

@app.route('/trash')
def trash():
    if 'admin' not in session:
        return redirect('/admin_login')
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PER_PAGE
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM shipments WHERE is_deleted=1")
    total_items = cur.fetchone()['cnt']
    total_pages = max(1, (total_items + PER_PAGE - 1) // PER_PAGE)
    cur.execute("SELECT * FROM shipments WHERE is_deleted=1 LIMIT ? OFFSET ?", (PER_PAGE, offset))
    shipments = cur.fetchall()
    conn.close()
    rows = ""
    for s in shipments:
        rows += f"""<tr>
          <td>{s['Sl_No']}</td><td>{s['Date_sent'] or ''}</td><td>{s['Model'] or ''}</td>
          <td>{s['Part_Number'] or ''}</td><td>{s['Part_Name'] or ''}</td>
          <td>{s['Supplier_name'] or ''}</td><td>{s['status'] or ''}</td>
          <td>
            <a href="{url_for('restore_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-success">Restore</a>
            <a href="{url_for('permanent_delete_shipment', slno=s['Sl_No'])}" class="btn btn-sm btn-danger"
               onclick="return confirm('Permanently delete?')">Delete Forever</a>
          </td></tr>"""
    pagination = "".join([f'<a href="?page={p}" class="{"active" if p == page else ""}">{p}</a>' for p in range(1, total_pages + 1)])
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
    if 'admin' not in session:
        return redirect('/admin_login')
    conn = get_db()
    conn.execute("UPDATE shipments SET is_deleted=0 WHERE Sl_No=?", (slno,))
    conn.commit()
    conn.close()
    return redirect('/trash')

@app.route('/permanent_delete_shipment/<int:slno>')
def permanent_delete_shipment(slno):
    if 'admin' not in session:
        return redirect('/admin_login')
    conn = get_db()
    conn.execute("DELETE FROM shipments WHERE Sl_No=?", (slno,))
    conn.commit()
    conn.close()
    return redirect('/trash')

# =========================================================
# DISCUSSION — WhatsApp style
# =========================================================
@app.route('/discussion/<int:shipment_id>', methods=['GET', 'POST'])
def view_discussion(shipment_id):
    if 'admin' not in session and 'dealer' not in session:
        return redirect('/')
    name, username, role = get_current_user()
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action', 'post')
        if action == 'post':
            cur.execute("""INSERT INTO Discussion
            (shipment_id,pi_number,message,dept,created_at,author_name,author_username,author_role)
            VALUES(?,?,?,?,?,?,?,?)""",
            (shipment_id, request.form.get('pi_number', ''), request.form.get('message', ''),
             role, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             name, username, role))
            conn.commit()
        elif action == 'edit':
            disc_id = int(request.form.get('disc_id', 0))
            cur.execute("SELECT * FROM Discussion WHERE Sl_No=?", (disc_id,))
            disc = cur.fetchone()
            if disc and (disc['author_username'] == username or 'admin' in session):
                cur.execute("UPDATE Discussion SET message=?,edited=1,edited_at=?,edited_by=? WHERE Sl_No=?",
                    (request.form.get('message', ''), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     f"{name} ({username})", disc_id))
                conn.commit()
        elif action == 'delete':
            disc_id = int(request.form.get('disc_id', 0))
            cur.execute("SELECT * FROM Discussion WHERE Sl_No=?", (disc_id,))
            disc = cur.fetchone()
            if disc and (disc['author_username'] == username or 'admin' in session):
                cur.execute("UPDATE Discussion SET is_deleted=1,edited_by=?,edited_at=? WHERE Sl_No=?",
                    (f"Deleted by {name} ({username})", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disc_id))
                conn.commit()
    cur.execute("SELECT * FROM shipments WHERE Sl_No=?", (shipment_id,))
    shipment = cur.fetchone()
    cur.execute("SELECT * FROM Discussion WHERE shipment_id=? ORDER BY Sl_No ASC", (shipment_id,))
    discussions = cur.fetchall()
    conn.close()
    back_link = '/admin_dashboard' if 'admin' in session else '/dealer_dashboard'

    disc_html = ""
    for d in discussions:
        is_mine = (d['author_username'] == username)
        can_edit = is_mine or 'admin' in session
        deleted = d['is_deleted'] == 1
        role_cls = ''.join(c for c in (d['author_role'] or 'user') if c.isalnum())

        # Admin roles go left, users go right
        author_role = d['author_role'] or ''
        is_admin_role = author_role in ('QACAdmin', 'QICAdmin', 'ProductionAdmin')
        side = 'left' if is_admin_role else 'right'

        edited_tag = f'<span class="edited-tag">&#9998; edited {d["edited_at"] or ""}</span>' if d['edited'] and not deleted else ""

        if deleted:
            bubble_extra = 'deleted-bubble'
            msg_content = "&#128465; This message was deleted"
            deleted_by = f'<div class="bubble-time"><span style="color:#f07070;font-size:.69rem">{d["edited_by"] or "Deleted"} &bull; {d["edited_at"] or ""}</span></div>'
            actions_html = ""
            edit_form = ""
        else:
            bubble_extra = ''
            msg_content = d['message'] or ''
            deleted_by = ""
            edit_form = ""
            if can_edit:
                edit_form = f"""
                <div id="ef-{d['Sl_No']}" class="bubble-edit-form" style="display:none">
                  <form method="POST">
                    <input type="hidden" name="action" value="edit">
                    <input type="hidden" name="disc_id" value="{d['Sl_No']}">
                    <textarea name="message" rows="2" style="width:100%">{d['message']}</textarea><br>
                    <button type="submit" class="btn btn-sm btn-primary" style="margin-top:4px">Save</button>
                    <button type="button" class="btn btn-sm" style="background:rgba(42,106,191,0.15);color:var(--chrome-2);border:1px solid var(--border-light);margin-top:4px"
                      onclick="document.getElementById('ef-{d['Sl_No']}').style.display='none'">Cancel</button>
                  </form>
                </div>"""
                actions_html = f"""
                <div class="bubble-actions">
                  <button type="button" class="btn btn-sm btn-warn"
                    onclick="document.getElementById('ef-{d['Sl_No']}').style.display='block'">&#9998; Edit</button>
                  <form method="POST" style="display:inline">
                    <input type="hidden" name="action" value="delete">
                    <input type="hidden" name="disc_id" value="{d['Sl_No']}">
                    <button type="submit" class="btn btn-sm btn-danger"
                      onclick="return confirm('Delete this message?')">&#128465; Delete</button>
                  </form>
                </div>"""
            else:
                actions_html = ""

        pi_badge = f'<span class="bubble-pi">PI: {d["pi_number"]}</span>' if d['pi_number'] else ''

        disc_html += f"""
        <div class="chat-bubble-wrap {side}">
          <div class="chat-bubble {side} {bubble_extra}">
            <div class="bubble-header">
              <span class="bubble-author">{d['author_name'] or 'Unknown'}</span>
              <span class="role-tag role-{role_cls}">{d['author_role'] or 'User'}</span>
              {pi_badge}
            </div>
            <div style="line-height:1.55">{msg_content}</div>
            {deleted_by}
            <div class="bubble-time">
              <span>{'@' + (d['author_username'] or '')}</span>
              <span>&bull;</span>
              <span>{d['created_at'] or ''}</span>
              {edited_tag}
            </div>
            {actions_html}
            {edit_form}
          </div>
        </div>"""

    if not disc_html:
        disc_html = "<p style='color:var(--text-dim);text-align:center;padding:32px'>No messages yet. Be the first to post!</p>"

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
        <a href="/export_discussion/{shipment_id}" class="btn btn-success">&#11015; Export to Excel</a>
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
          </div>
          <div class="form-group" style="margin-top:10px"><label>Message</label>
            <textarea name="message" rows="3" style="width:100%" required placeholder="Type your message..."></textarea></div>
          <button type="submit" class="btn btn-primary" style="margin-top:10px">&#128228; Post Message</button>
        </form>
      </div>
      <div class="card">
        <h3>Messages ({msg_count})</h3>
        <div class="chat-container" style="margin-top:10px" id="chatbox">{disc_html}</div>
      </div>
    </div>
    <script>
      var chatbox = document.getElementById('chatbox');
      if(chatbox) chatbox.scrollTop = chatbox.scrollHeight;
    </script>"""
    return render_template_string(html)

# =========================================================
# MANAGE ADMINS
# =========================================================
@app.route('/manage_admins', methods=['GET', 'POST'])
def manage_admins():
    if 'admin' not in session:
        return redirect('/admin_login')
    conn = get_db()
    cur = conn.cursor()
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            try:
                cur.execute("INSERT INTO admins(name,username,password,role) VALUES(?,?,?,?)",
                    (request.form['name'], request.form['username'], request.form['password'], request.form['role']))
                conn.commit()
                msg = "add_ok"
            except Exception:
                msg = "add_err"
        elif action == 'delete':
            aid = int(request.form.get('admin_id', 0))
            if aid != session['admin']:
                cur.execute("DELETE FROM admins WHERE Sl_No=?", (aid,))
                conn.commit()
                msg = "del_ok"
            else:
                msg = "del_self"
        elif action == 'change_password':
            cur.execute("UPDATE admins SET password=? WHERE Sl_No=?",
                (request.form['new_password'], int(request.form.get('admin_id', 0))))
            conn.commit()
            msg = "pw_ok"
    cur.execute("SELECT * FROM admins ORDER BY Sl_No")
    admins = cur.fetchall()
    conn.close()
    alert_map = {
        'add_ok': ('success', 'Admin added successfully.'),
        'add_err': ('danger', 'Username already exists.'),
        'del_ok': ('success', 'Admin deleted.'),
        'del_self': ('danger', 'Cannot delete your own account.'),
        'pw_ok': ('success', 'Password updated.'),
    }
    alert_html = ""
    if msg in alert_map:
        cls, text = alert_map[msg]
        alert_html = f'<div class="alert alert-{cls}">{text}</div>'
    rows = ""
    for a in admins:
        role_cls = ''.join(c for c in a['role'] if c.isalnum())
        you = " <small style='color:var(--accent-gold)'>(you)</small>" if a['Sl_No'] == session['admin'] else ""
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
            {"" if a['Sl_No'] == session['admin'] else f"""
            <form method="POST" style="display:inline">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="admin_id" value="{a['Sl_No']}">
              <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Delete admin?')">Delete</button>
            </form>"""}
          </td></tr>"""
    role_opts = "".join([f'<option value="{r}">{r}</option>' for r in ['QACAdmin', 'QICAdmin', 'ProductionAdmin']])
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
@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'admin' not in session:
        return redirect('/admin_login')
    conn = get_db()
    cur = conn.cursor()
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            cur.execute("DELETE FROM dealers WHERE Sl_No=?", (int(request.form.get('user_id', 0)),))
            conn.commit()
            msg = "del_ok"
        elif action == 'change_password':
            cur.execute("UPDATE dealers SET password=? WHERE Sl_No=?",
                (request.form['new_password'], int(request.form.get('user_id', 0))))
            conn.commit()
            msg = "pw_ok"
    cur.execute("SELECT * FROM dealers ORDER BY Sl_No")
    users = cur.fetchall()
    conn.close()
    alert_html = ""
    if msg == 'del_ok':
        alert_html = '<div class="alert alert-success">User deleted.</div>'
    elif msg == 'pw_ok':
        alert_html = '<div class="alert alert-success">Password updated.</div>'
    rows = ""
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
TKM
