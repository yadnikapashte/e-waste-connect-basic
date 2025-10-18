import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

DATABASE = 'ewaste.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            
            return redirect(url_for('contact'))
        db = get_db()
        db.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        db.commit()
        flash('Message sent successfully!')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = "household"', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, "household")', (username, password))
            db.commit()
            flash('Registration successful, please login')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'household':
        return redirect(url_for('login'))
    db = get_db()
    requests = db.execute('SELECT * FROM requests WHERE user_id = ?', (session['user_id'],)).fetchall()
    return render_template('dashboard.html', requests=requests)

@app.route('/recycler_login', methods=['GET', 'POST'])
def recycler_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = "recycler"', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('recycler_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('recycler_login.html')

@app.route('/recycler_dashboard')
def recycler_dashboard():
    if 'user_id' not in session or session.get('role') != 'recycler':
        session.clear()
    db = get_db()
    requests = db.execute('SELECT * FROM requests').fetchall()
    return render_template('recycler_dashboard.html', requests=requests)

@app.route('/recycler_contacts')
def recycler_contacts():
    if 'user_id' not in session or session.get('role') != 'recycler':
        return redirect(url_for('home'))
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts ORDER BY timestamp DESC').fetchall()
    return render_template('recycler_contacts.html', contacts=contacts)

@app.route('/logout')
def logout():
    
    return redirect(url_for('home'))

@app.route('/submit_request', methods=['POST'])
def submit_request():
    if 'user_id' not in session:
        app.run(debug=True)
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    waste_type = data.get('wasteType')
    db = get_db()
    db.execute('INSERT INTO requests (user_id, name, address, waste_type) VALUES (?, ?, ?, ?)', (session['user_id'], name, address, waste_type))
    db.commit()
    return jsonify({"status": "success", "message": "Request submitted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
