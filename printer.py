import mysql.connector
import csv
from fpdf import FPDF

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
   
    # Update the user's print count and store the purpose
    cursor.execute("INSERT INTO print_jobs (user_id, pages, purpose) VALUES (%s, %s, %s)",
                   (logged_in_user_id, pages, purpose))
    connection.commit()
    print(f"{pages} pages printed by user {logged_in_user_id} for {purpose}.")
   
    cursor.close()
    connection.close()

def add_user():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    user_id = input("Enter new User ID: ")
    department = input("Enter Department: ")
    password = input("Enter Password: ")
    
    try:
        cursor.execute("INSERT INTO users (user_id, department, password) VALUES (%s, %s, %s)", (user_id, department, password))
        connection.commit()
        print(f"User {user_id} added successfully.")
    except mysql.connector.IntegrityError:
        print(f"User {user_id} already exists.")
    
    cursor.close()
    connection.close()

# Edit an Existing User (Admin Only)
def edit_user():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    user_id = input("Enter the User ID to edit: ")
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    
    if result:
        new_department = input("Enter new Department: ")
        new_password = input("Enter new Password: ")
        cursor.execute("UPDATE users SET department = %s, password = %s WHERE user_id = %s", 
                       (new_department, new_password, user_id))
        connection.commit()
        print(f"User {user_id} updated successfully.")
    else:
        print(f"User {user_id} not found.")
    
    cursor.close()
    connection.close()

# Delete a User (Admin Only)
def delete_user():
    connection = connect_to_database()
    cursor = connection.cursor()
    
    user_id = input("Enter the User ID to delete: ")
    
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    connection.commit()
    
    if cursor.rowcount > 0:
        print(f"User {user_id} deleted successfully.")
    else:
        print(f"User {user_id} not found.")
    
    cursor.close()
    connection.close()

# User login function
def login():
    user_id = input("Enter User ID: ")
    password = input("Enter Password: ")
   
    connection = connect_to_database()
    cursor = connection.cursor()
   
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND password = %s", (user_id, password))
    result = cursor.fetchone()
   
    if result:
        print(f"Login successful. Welcome, User {user_id}.")
        return user_id
    else:
        print("Invalid user ID or password. Please try again.")
        return None
   
    cursor.close()
    connection.close()

# Export print records as CSV (Admin only)
def export_to_csv():
    connection = connect_to_database()
    cursor = connection.cursor()
   
    cursor.execute("SELECT * FROM print_jobs")
    rows = cursor.fetchall()
   
    with open('print_jobs.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['User ID', 'Pages', 'Purpose', 'Timestamp'])
        writer.writerows(rows)
   
    print("Print job data has been exported to print_jobs.csv.")
   
    cursor.close()
    connection.close()

# Export print records as PDF (Admin only)
def export_to_pdf():
    connection = connect_to_database()
    cursor = connection.cursor()
   
    cursor.execute("SELECT * FROM print_jobs")
    rows = cursor.fetchall()
   
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
   
    pdf.cell(200, 10, txt="Print Job Records", ln=True, align='C')
   
    for row in rows:
        pdf.cell(200, 10, txt=f"User ID: {row[0]} | Pages: {row[1]} | Purpose: {row[2]} | Timestamp: {row[3]}", ln=True)
   
    pdf.output("print_jobs.pdf")
    print("Print job data has been exported to print_jobs.pdf.")
   
    cursor.close()
    connection.close()

# View User Details (Admin only)
def view_user_details():
    connection = connect_to_database()
    cursor = connection.cursor()
   
    cursor.execute("SELECT user_id, department, print_count FROM users")
    users = cursor.fetchall()
   
    if users:
        print(f"\n--- Total Users: {len(users)} ---")
        for user in users:
            print(f"User ID: {user[0]} | Department: {user[1]} | Total Pages Printed: {user[2]}")
    else:
        print("No users found.")
   
    cursor.close()
    connection.close()

# Admin login
def admin_login():
    admin_id = input("Enter Admin ID: ")
    admin_password = input("Enter Admin Password: ")
   
    if admin_id == ADMIN_ID and admin_password == ADMIN_PASSWORD:
        print("Admin login successful.")
        return True
    else:
        print("Invalid Admin ID or Password.")
        return False

# Admin functionalities
def admin_panel():
    while True:
        print("\n--- Admin Panel ---")
        print("1. Export Print Jobs to CSV")
        print("2. Export Print Jobs to PDF")
        print("3. View User Details")
        print("4. Add User")
        print("5. Edit User")
        print("6. Delete User")
        print("7. Logout")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == '1':
            export_to_csv()
        
        elif choice == '2':
            export_to_pdf()
        
        elif choice == '3':
            view_user_details()
        
        elif choice == '4':
            add_user()
        
        elif choice == '5':
            edit_user()
        
        elif choice == '6':
            delete_user()
        
        elif choice == '7':
            print("Logging out from Admin Panel.")
            break
        
        else:
            print("Invalid choice! Please select a valid option.")

# Main Function for User
def user_functionality():
    logged_in_user_id = login()
    if logged_in_user_id:
        pages = int(input("Enter number of pages to print: "))
        purpose = input("Enter the purpose of the printout: ")
        record_print(logged_in_user_id, pages, purpose)


# Main Menu Loop
while True:
    print("\n--- Printer Management System ---")
    print("1. User Login")
    print("2. Admin Login")
    print("3. Exit")
   
    choice = input("Enter your choice (1-3): ")
   
    if choice == '1':
        user_functionality()
   
    elif choice == '2':
        if admin_login():
            admin_panel()
   
    elif choice == '3':
        print("Exiting the Printer Management System. Goodbye!")
        break
   
    else:
        print("Invalid choice! Please select a valid option.")
