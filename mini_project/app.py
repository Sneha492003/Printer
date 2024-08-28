from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.your-email-provider.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


# Admin credentials
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

# Database Connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sneha",
        database="printer"
    )

# Hash the password before storing
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Check password hash
def check_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP to Email
def send_otp(email, otp):
    msg = Message('Your OTP', sender='your-email@example.com', recipients=[email])
    msg.body = f"Your OTP for login is: {otp}"
    mail.send(msg)

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
        cursor.execute("SELECT user_id, password, email FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        if result and check_password(result[1], password):
            session['user_id'] = user_id
            otp = generate_otp()
            session['otp'] = otp
            send_otp(result[2], otp)
            return redirect(url_for('verify_otp'))
        else:
            flash('Invalid user ID or password')
        
        cursor.close()
        connection.close()
        
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        otp = request.form['otp']
        
        if otp == session.get('otp'):
            session.pop('otp', None)
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid OTP. Please try again.')

    return render_template('verify_otp.html')

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
    
    connection = connect_to_database()
    cursor = connection.cursor()
    
    cursor.execute("SELECT user_id, department, print_count FROM users")
    users = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return render_template('admin_panel.html', users=users)

@app.route('/edit_user/<user_id>', methods=['POST'])
def edit_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Your edit user logic here
    
    return redirect(url_for('admin_panel'))

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    connection = connect_to_database()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return redirect(url_for('admin_panel'))

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
