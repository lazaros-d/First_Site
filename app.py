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
        c.execute('''
                  
            CREATE TABLE subjects (
                subject_name TEXT PRIMARY KEY UNIQUE NOT NULL,
                subject_semester INTEGER
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

def create_subjects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executemany("""
              INSERT OR UPDATE INTO subjects (subject_name, subject_semester) VALUES (?, ?)
            """, [
              ('ΕΙΣΑΓΩΓΗ ΣΤΟΥΣ ΥΠΟΛΟΓΙΣΤΕΣ', '1'),
              ('ΕΙΣΑΓΩΓΗ ΣΤΟΝ ΠΡΟΓΡΑΜΜΑΤΙΣΜΜΟ ΥΠΟΛΟΓΙΣΤΩΝ', '1'),
              ('ΜΑΘΗΜΑΤΙΚΗ ΑΝΑΛΥΣΗ 1', '1'),
              ('ΗΛΕΚΤΡΟΜΑΓΝΗΤΙΣΜΟΣ-ΦΥΣΙΚΗ', '1'),
              ('ΗΛΕΚΤΡΟΝΙΚΗ', '1'),
              ('ΔΙΑΚΡΙΤΑ ΜΑΘΗΜΑΤΙΚΑ', '1'),

              ('ΛΕΙΤΟΥΡΓΙΚΑ ΣΥΣΤΗΜΑΤΑ', '2'),
              ('ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΑΦΗΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟς ΥΠΟΛΟΓΙΣΤΩΝ C++', '2'),
              ('ΜΑΘΗΜΑΜΤΙΚΗ ΑΝΑΛΥΣΗ 2', '2'),
              ('ΓΡΑΜΜΙΚΗ ΑΛΓΕΒΡΑ', '2'),
              ('ΣΥΝΔΥΑΣΤΙΚΑ ΨΗΦΙΑΚΑ ΗΛΕΚΤΡΟΝΙΚΑ', '2'),
              ('ΑΓΓΛΙΚΑ ΟΡΟΛΟΓΙΑ ΠΛΗΡΟΦΟΡΙΚΗΣ 1', '2'),

              ('ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ ΣΤΟ ΔΙΑΔΥΚΤΥΟ', '3'),
              ('ΜΕΤΑΓΛΩΤΤΙΣΤΕΣ', '3'),
              ('ΑΡΙΘΜΗΤΙΚΗ ΑΝΑΛΥΣΗ', '3'),
              ('ΠΙΘΑΝΟΤΗΤΕΣ-ΣΤΑΤΙΣΤΙΚΗ', '3'),
              ('ΑΚΟΛΟΥΘΙΑΚΑ ΨΗΦΙΑΚΑ ΗΛΕΚΤΡΟΝΙΚΑ', '3'),
              ('ΑΓΓΛΙΚΑ ΟΡΟΛΟΓΙΑ ΠΛΗΡΟΦΟΡΙΚΗΣ 2', '3'),

              ('ΔΙΚΤΥΑ ΥΠΟΛΟΓΙΣΤΩΝ', '4'),
              ('ΒΑΣΕΙΣ ΔΕΔΟΜΕΝΩΝ', '4'),
              ('ΜΙΚΡΟΕΠΕΞΕΡΓΑΣΤΕΣ-ΜΙΚΡΟΕΛΕΓΚΤΕΣ 1', '4'),
              ('ΑΡΧΙΤΕΚΤΟΝΙΚΗ ΥΠΟΛΟΓΙΣΤΩΝ', '4'),
              ('ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΕΦΗΣ ΑΝΑΠΤΥΞΗ ΕΦΑΡΜΟΓΩΝ ΜΕ JAVA', '4'),
              ('ΔΟΜΕΣ ΔΕΔΟΜΕΝΩΝ', '4'),

              ('ΚΑΤΑΝΕΜΗΜΕΝΑ ΣΥΣΤΗΜΑΤΑ', '5'),
              ('ΑΛΓΟΡΙΘΜΟΙ ΚΑΙ ΠΟΛΥΠΛΟΚΟΤΗΤΑ', '5'),
              ('ΤΕΧΝΟΛΟΓΙΑ ΛΟΓΙΣΜΙΚΟΥ', '5'),
              ('ΣΧΕΔΙΑΣΗ ΔΙΚΤΥΩΝ ΥΠΟΛΟΓΙΣΤΩΝ', '5'),
              ('ΕΙΔΙΚΑ ΘΕΜΑΤΑ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΥ', '5'),
              ('ΕΦΑΡΜΟΣΜΕΝΑ ΜΑΘΗΜΑΤΙΚΑ', '5'),
              ('ΤΕΧΝΟΛΟΓΙΑ ΠΟΛΥΜΕΣΩΝ', '5'),
              ('ΑΛΛΗΛΕΠΙΔΡΑΣΗ ΑΝΘΡΩΠΟΥ-ΜΗΧΑΝΗΣ', '5'),
              ('ΘΕΩΡΙΑ ΑΡΙΘΜΩΝ', '5'),

              ('ΑΣΦΑΛΕΙΑ ΥΠΟΛΟΓΙΣΤΗΚΩΝ ΣΥΣΤΗΜΑΤΩΝ', '6'),
              ('ΤΕΧΝΗΤΗ ΝΟΗΜΟΣΥΝΗ', '6'),
              ('ΤΗΛΕΠΙΚΟΙΝΩΝΙΕΣ', '6'),
              ('ΣΧΕΔΙΑΣΗ ΨΗΦΙΑΚΩΝ ΣΥΣΤΗΜΑΤΩΝ ΜΕ VHDL', '6'),
              ('ΑΣΥΡΜΑΤΕΣ ΚΙΝΗΤΕΣ ΕΠΙΚΟΙΝΩΝΙΕΣ', '6'),
              ('ΓΡΑΦΙΚΑ ΜΕ ΥΠΟΛΟΓΙΣΤΕΣ', '6'),
              ('ΠΡΟΧΩΡΗΜΕΝΑ ΘΕΜΑΤΑ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΥ ΙΣΤΟΥ 1', '6'),
              ('ΕΔΙΚΑ ΘΕΜΑΤΑ ΔΙΚΤΥΩΝ 1', '6'),
              ('ΥΠΟΛΟΓΙΣΤΙΚΑ ΝΕΦΗ', '6'),
              ('ΘΕΜΑΤΑ ΑΡΙΘΜΗΤΙΚΗΣ ΑΝΑΛΥΣΗΣ', '6'),
              ('ΑΡΙΘΜΗΤΙΚΗ ΕΠΙΛΥΣΗ ΔΙΑΦΟΡΚΩΝ ΕΞΙΣΩΣΕΩΝ', '6'),

              ('ΕΡΕΥΝΗΤΙΚΗ ΜΕΘΟΔΟΛΟΓΙΑ ΚΑΙ ΔΕΟΝΤΟΛΟΓΙΑ', '7'),
              ('ΔΙΚΤΥΑ ΥΨΗΛΩΝ ΤΑΧΥΤΗΤΩΝ', '7'),
              ('ΠΡΟΧΩΡΗΜΕΝΑ ΘΕΜΜΑΤΑ ΒΑΣΕΩΝ ΔΕΔΟΜΕΝΩΝ', '7'),
              ('ΣΧΕΔΙΑΣΗ ΕΝΣΩΜΑΤΩΜΕΝΩΝ ΣΥΣΤΗΜΑΤΩΝ ΜΕ VLSI 1', '7'),
              ('ΤΕΧΝΟΛΟΓΙΕΣ ΔΙΑΔΙΚΤΥΟΥ ΚΑΙ ΚΙΝΗΤΟΣ ΥΠΟΛΟΓΙΣΜΟΣ', '7'),
              ('ΠΛΗΡΟΦΟΡΙΑΚΑ ΣΥΣΤΗΜΑΤΑ', '7'),
              ('ΠΡΟΧΩΡΗΜΕΝΑ ΘΕΜΑΤΑ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΥ ΙΣΤΟΥ 2', '7'),
              ('ΠΡΟΗΓΜΕΝΕΣ ΑΡΧΙΤΕΚΤΟΝΙΚΕΣ', '7'),
              ('ΕΙΔΙΚΑ ΘΕΜΑΤΑ ΔΙΚΤΥΩΝ 2', '7'),
              ('ΑΣΦΑΛΕΙΑ ΔΙΚΤΥΩΝ', '7'),
              ('ΑΛΓΟΡΙΘΜΟΙ ΜΗΧΑΝΙΚΗΣ ΜΑΘΗΣΗΣ', '7'),

              ('ΨΗΦΙΑΚΗ ΕΠΕΞΕΡΓΑΣΙΑ ΣΗΜΑΤΟΣ', '8'),
              ('ΟΠΤΙΚΟΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ', '8'),
              ('ΜΙΚΡΟΕΠΕΞΕΡΓΑΣΤΕΣ-ΜΙΚΡΟΕΛΕΓΚΤΕΣ 2', '8'),
              ('ΕΞΟΡΗΞΗ ΔΕΔΟΜΕΝΩΝ', '8'),
              ('ΚΡΥΠΤΟΓΡΑΦΙΑ', '8'),
              ('ΣΥΣΤΗΜΑΤΑ ΑΝΑΜΟΝΗΣ', '8'),
              ('ΕΠΙΧΕΙΡΗΣΙΑΚΗ ΕΡΕΥΝΑ', '8'),
              ('ΣΧΕΔΙΑΣΗ ΨΗΦΙΑΚΩΝ ΠΑΙΧΝΙΔΙΩΝ ΚΑΙ ΠΑΙΧΝΙΔΟΠΟΙΗΣΗ', '8'),
              ('ΟΠΤΙΚΕΣ ΕΠΙΚΟΙΝΩΝΙΕΣ', '8'),
              ('ΣΧΕΔΙΑΣΗ ΕΝΣΩΜΑΤΩΜΕΝΩΝ ΣΥΣΤΗΜΑΤΩΝ ΜΕ VLSI 2', '8'),
              ('ΣΧΕΔΙΑΣΗ ΚΑΙ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ ΕΝΣΩΜΑΤΩΜΕΝΩΝ ΣΥΣΤΗΜΑΤΩΝ', '8')

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

@app.route('/subjects', methods=['GET', 'POST'])
def subjects():

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM subjects")
    subject_names = c.fetchall()
    conn.close()

    return render_template('subjects.html', σθβξεψτναμε=subject_names)

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