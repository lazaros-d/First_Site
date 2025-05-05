from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # άλλαξέ το σε κάτι πιο ασφαλές στην παραγωγή

DB_PATH = 'database.db'

# Δημιουργία βάσης δεδομένων αν δεν υπάρχει
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
        conn.commit()
        conn.close()

# Δημιουργία superuser admin (αν δεν υπάρχει ήδη)
def create_superuser():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users (username, password, admin)
        VALUES (?, ?, ?)
    """, ("admin", "adminpassword", 1))
    conn.commit()
    if c.rowcount == 1:
        print("✅ Superuser created.")
    else:
        print("ℹ️ Superuser already exists.")
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            session['admin'] = bool(user[3])
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Λάθος στοιχεία")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], is_admin=session.get('admin', False))

# Εκκίνηση εφαρμογής
if __name__ == '__main__':
    init_db()
    create_superuser()
    app.run(debug=True)