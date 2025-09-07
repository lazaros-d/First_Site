from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mysecretkey'

DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            admin INTEGER DEFAULT 0
        )
    ''')

    # Subjects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE NOT NULL,
            subject_semester TEXT
        )
    ''')

    # Chat messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def create_superuser():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_pw = generate_password_hash("adminpassword")
    c.execute("INSERT OR IGNORE INTO users (username, password, admin) VALUES (?, ?, ?)", ("admin", hashed_pw, 1))
    conn.commit()
    conn.close()

def create_subjects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    subjects_list = [
        ('ΕΙΣΑΓΩΓΗ ΣΤΟΥΣ ΥΠΟΛΟΓΙΣΤΕΣ', '1'),
        ('ΕΙΣΑΓΩΓΗ ΣΤΟΝ ΠΡΟΓΡΑΜΜΑΤΙΣΜΜΟ ΥΠΟΛΟΓΙΣΤΩΝ', '1'),
        ('ΜΑΘΗΜΑΤΙΚΗ ΑΝΑΛΥΣΗ 1', '1'),
        ('ΗΛΕΚΤΡΟΜΑΓΝΗΤΙΣΜΟΣ-ΦΥΣΙΚΗ', '1'),
        ('ΗΛΕΚΤΡΟΝΙΚΗ', '1'),
        ('ΔΙΑΚΡΙΤΑ ΜΑΘΗΜΑΤΙΚΑ', '1'),
        ('ΛΕΙΤΟΥΡΓΙΚΑ ΣΥΣΤΗΜΑΤΑ', '2')
        # πρόσθεσε όσα θέλεις
    ]
    c.executemany("INSERT OR IGNORE INTO subjects (subject_name, subject_semester) VALUES (?, ?)", subjects_list)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Το όνομα χρήστη υπάρχει ήδη.")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/subjects')
def subjects():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, subject_semester, subject_name FROM subjects")
    rows = c.fetchall()
    conn.close()

    subjects_by_semester = {}
    for id_, semester, name in rows:
        subjects_by_semester.setdefault(semester, []).append((id_, name))

    return render_template('subjects.html', subjects_by_semester=subjects_by_semester)

@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    # εδώ θα εμφανιστεί το υλικό του μαθήματος
    return f"Υλικό για μάθημα ID {subject_id}"

# Chat endpoints
@app.route('/chat/messages')
def get_chat_messages():
    if 'username' not in session:
        return jsonify({'error': 'Δεν είστε συνδεδεμένοι'}), 401

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM chat_messages ORDER BY id ASC")
    messages = c.fetchall()
    conn.close()

    return jsonify([{'username': u, 'message': m, 'timestamp': t} for u, m, t in messages])

@app.route('/chat', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'error': 'Δεν είστε συνδεδεμένοι'}), 401

    message = request.form.get('message')
    username = session['username']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message and message.strip():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO chat_messages (username, message, timestamp) VALUES (?, ?, ?)",
                  (username, message.strip(), timestamp))
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Το μήνυμα είναι κενό'}), 400

if __name__ == '__main__':
    init_db()
    create_superuser()
    create_subjects()
    app.run(debug=True, port=5001)
