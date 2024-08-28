from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import csv
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sneha",
        database="printer"
    )

# Admin credentials
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

# Record Prints with Logged-in User ID
def record_print(logged_in_user_id, pages, purpose):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO print_jobs (user_id, pages, purpose) VALUES (%s, %s, %s)", 
                   (logged_in_user_id, pages, purpose))
    connection.commit()
    cursor.close()
    connection.close()

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND password = %s", (user_id, password))
        result = cursor.fetchone()
        
        if result:
            session['user_id'] = user_id
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid user ID or password')
        
        cursor.close()
        connection.close()
        
    return render_template('login.html')

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        pages = request.form['pages']
        purpose = request.form['purpose']
        record_print(session['user_id'], pages, purpose)
        flash('Print job recorded successfully')
    
    return render_template('user_dashboard.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        admin_password = request.form['admin_password']
        
        if admin_id == ADMIN_ID and admin_password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid Admin ID or Password')
        
    return render_template('admin_login.html')

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_panel.html')

@app.route('/export_csv')
def export_csv():
    # CSV export logic
    return redirect(url_for('admin_panel'))

@app.route('/export_pdf')
def export_pdf():
    # PDF export logic
    return redirect(url_for('admin_panel'))

@app.route('/view_users')
def view_users():
    # View user details logic
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
