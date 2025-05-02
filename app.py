from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

# Δημιουργία Flask εφαρμογής
app = Flask(__name__)
app.secret_key = 'secret_key_for_sessions'  # Μυστικό κλειδί για sessions

# Συνάρτηση για να δημιουργήσει τη βάση αν δεν υπάρχει
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            admin INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Εκτελούμε τη δημιουργία της βάσης όταν ξεκινά η εφαρμογή
init_db()

# Συνάρτηση για να δημιουργηθεί ο superuser (admin) αν δεν υπάρχει
def create_superuser():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Έλεγχος αν υπάρχει ήδη ο χρήστης admin
    c.execute('SELECT * FROM users WHERE username = "admin"')
    superuser = c.fetchone()
    
    # Αν δεν υπάρχει, τον δημιουργούμε
    if superuser is None:
        c.execute("INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", ("admin", "adminpassword", 1))
        conn.commit()
        print("Superuser created.")
    else:
        print("Superuser already exists.")
        
    conn.close()

create_superuser()

# Route: Αρχική σελίδα
@app.route('/')
def home():
    return render_template('home.html')

# Route: Εγγραφή χρήστη
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", (username, password, 0))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Το όνομα χρήστη χρησιμοποιείται ήδη!"
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

# Route: Σύνδεση χρήστη
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Λάθος όνομα χρήστη ή κωδικός!"

    return render_template('login.html')

# Route: Dashboard μετά το login
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[3] == 1:  # Αν ο χρήστης είναι admin
            return f"Γεια σου {username}! Καλωσήρθες στο Admin Dashboard!"
        else:
            return f"Γεια σου {username}! Καλωσήρθες στο Dashboard!"
    else:
        return redirect(url_for('login'))

# Route: Admin Panel για διαχείριση χρηστών
@app.route('/admin', methods=['GET'])
def admin_panel():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user and user[3] == 1:  # Ελέγχουμε αν είναι admin
            c.execute("SELECT * FROM users")  # Φέρνουμε όλους τους χρήστες
            users = c.fetchall()
            conn.close()
            return render_template('admin_panel.html', users=users)
        else:
            conn.close()
            return "Δεν έχετε πρόσβαση σε αυτήν τη σελίδα."
    else:
        return redirect(url_for('login'))

# Τρέχουμε τον server
if __name__ == "__main__":
    app.run(debug=True)