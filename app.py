from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_mail import Mail, Message
import os
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gharalsandesh1@gmail.com'
app.config['MAIL_PASSWORD'] = 'frquobnskpdqgmjh'
mail = Mail(app)

# Database setup
def init_db():
    with sqlite3.connect('mcq.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_option INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                expiration DATETIME NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mcq/<language>')
def language_tests(language):
    modules = {
        'Python': ['Numpy', 'Pandas', 'Matplotlib'],
        'JavaScript': ['Basics', 'DOM', 'ES6'],
        'Java': ['OOP', 'Collections', 'Streams'],
        'C++':['Pointer']
    }
    return render_template('language_tests.html', language=language, modules=modules.get(language, []))

@app.route('/mcq/<language>/<module>')
def mcq_test(language, module):
    with sqlite3.connect('mcq.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions WHERE module = ?', (module,))
        questions = cursor.fetchall()
    return render_template('mcq_test.html', questions=questions, language=language, module=module)

@app.route('/tutorials')
def tutorials():
    # You can add logic to fetch tutorial data from a database if needed
    return render_template('tutorials.html')
@app.route('/tutorials/introduction-to-python')
def introduction_to_python():
    return render_template('Tutorials/introduction_to_python.html')

@app.route('/submit/<language>/<module>', methods=['POST'])
def submit(language, module):
    if request.method == 'POST':
        answers = request.form.to_dict()
        score = 0
        total = len(answers)
        wrong_answers = []

        with sqlite3.connect('mcq.db') as conn:
            cursor = conn.cursor()
            for question_id, answer in answers.items():
                cursor.execute('SELECT question, correct_option, option1, option2, option3, option4 FROM questions WHERE id = ?', (question_id,))
                question_data = cursor.fetchone()
                question, correct_option, option1, option2, option3, option4 = question_data
                correct_answer = [option1, option2, option3, option4][correct_option - 1]
                user_answer = [option1, option2, option3, option4][int(answer) - 1]

                if int(answer) == correct_option:
                    score += 1
                else:
                    wrong_answers.append((question, user_answer, correct_answer))

        return render_template('result.html', score=score, total=total, language=language, module=module, wrong_answers=wrong_answers)
@app.route('/Tests')
def Tests():
    return render_template('Tests.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/resources')
def resources():
    return render_template('resources.html')


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        with sqlite3.connect('mcq.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
            conn.commit()
        return render_template('contact.html', success=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        
        with sqlite3.connect('mcq.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (userid,))
            user = cursor.fetchone()
            
            if user and user[2] == password:  # Assuming password is the third column in the users table
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return redirect(url_for('login'))
                
    return render_template('LOGIN/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('mcq.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists.', 'danger')
                return redirect(url_for('register'))
    return render_template('LOGIN/register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        token = secrets.token_urlsafe(16)
        expiration = datetime.now() + timedelta(hours=1)
        
        with sqlite3.connect('mcq.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            if user:
                cursor.execute('INSERT INTO reset_tokens (email, token, expiration) VALUES (?, ?, ?)', (email, token, expiration))
                conn.commit()
                
                reset_link = url_for('reset_password', token=token, _external=True)
                msg = Message("Password Reset Request", sender='gharalsandesh1@gmail.com', recipients=[email])
                msg.body = f'To reset your password, click the following link: {reset_link}'
                mail.send(msg)
                
                flash('Password reset link has been sent to your email.', 'info')
                return redirect(url_for('login'))
            else:
                flash('Email not found. Please try again.', 'danger')
                return redirect(url_for('forgot_password'))
    return render_template('LOGIN/forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    with sqlite3.connect('mcq.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reset_tokens WHERE token = ? AND expiration > ?', (token, datetime.now()))
        token_data = cursor.fetchone()
        if not token_data:
            flash('Invalid or expired token. Please try again.', 'danger')
            return redirect(url_for('forgot_password'))
        
        email = token_data[1]
        
        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
                cursor.execute('DELETE FROM reset_tokens WHERE token = ?', (token,))
                conn.commit()
                flash('Password has been updated. Please log in with your new password.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match. Please try again.', 'danger')
                return redirect(url_for('reset_password', token=token))
    
    return render_template('LOGIN/reset_password.html', token=token)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
