from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # ⚠️ Άλλαξέ το σε ασφαλές κλειδί στην παραγωγή

DB_PATH = 'database.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                admin INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE NOT NULL,
                subject_semester TEXT
            )
        ''')
        conn.commit()
        conn.close()

def create_superuser():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_pw = generate_password_hash("adminpassword")
    c.execute("""
        INSERT OR IGNORE INTO users (username, password, admin)
        VALUES (?, ?, ?)
    """, ("admin", hashed_pw, 1))
    conn.commit()
    conn.close()

def create_subjects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE,
            subject_semester TEXT
        )
    """)
    c.executemany("""
        INSERT OR IGNORE INTO subjects (subject_name, subject_semester)
        VALUES (?, ?)
    """, [
        ('ΕΙΣΑΓΩΓΗ ΣΤΟΥΣ ΥΠΟΛΟΓΙΣΤΕΣ', '1'),
        ('ΕΙΣΑΓΩΓΗ ΣΤΟΝ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟ ΥΠΟΛΟΓΙΣΤΩΝ', '1'),
        ('ΜΑΘΗΜΑΤΙΚΗ ΑΝΑΛΥΣΗ 1', '1'),
        ('ΗΛΕΚΤΡΟΜΑΓΝΗΤΙΣΜΟΣ-ΦΥΣΙΚΗ', '1'),
        ('ΗΛΕΚΤΡΟΝΙΚΗ', '1'),
        ('ΔΙΑΚΡΙΤΑ ΜΑΘΗΜΑΤΙΚΑ', '1'),
        ('ΛΕΙΤΟΥΡΓΙΚΑ ΣΥΣΤΗΜΑΤΑ', '2'),
        ('ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΑΦΗΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ ΥΠΟΛΟΓΙΣΤΩΝ C++', '2'),
        ('ΜΑΘΗΜΑΤΙΚΗ ΑΝΑΛΥΣΗ 2', '2'),
        # Προσθέτεις τα υπόλοιπα όπως είχες ήδη
    ])
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Το όνομα χρήστη υπάρχει ήδη.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            session['admin'] = bool(user[3])
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Λάθος στοιχεία")
    return render_template('login.html')

@app.route('/subjects')
def subjects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT subject_name, subject_semester FROM subjects")
    rows = c.fetchall()
    conn.close()

    subjects_by_semester = {}
    for name, semester in rows:
        subjects_by_semester.setdefault(semester, []).append(name)

    return render_template('subjects.html', subjects_by_semester=subjects_by_semester)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], is_admin=session.get('admin', False))

if __name__ == '__main__':
    init_db()
    create_superuser()
    create_subjects()
    app.run(debug=True)