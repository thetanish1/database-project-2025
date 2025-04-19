import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# Database connection function
def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",  # Use your MySQL password
        database="department_management"
    )

# Login function
def login():
    username = entry_username.get()
    password = entry_password.get()

    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = cursor.fetchone()
    if user:
        messagebox.showinfo("Login Success", "Login Successful!")
        root.destroy()
        open_dashboard(user[3])  # user[3] is the role (HOD, Faculty, or Student)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials!")
    cursor.close()
    connection.close()

# Open dashboard based on role
def open_dashboard(role):
    dashboard = tk.Tk()
    dashboard.title(f"{role} Dashboard")

    # Tabs for different roles
    tabControl = ttk.Notebook(dashboard)

    if role == "HOD":
        # HOD Tab: Assign work to teachers and students
        faculty_tab = ttk.Frame(tabControl)
        tabControl.add(faculty_tab, text="Faculty Assignment")
        tabControl.pack(expand=1, fill="both")

        # HOD functionality: Assign work to faculty
        assign_faculty_label = tk.Label(faculty_tab, text="Assign Work to Faculty")
        assign_faculty_label.pack()
        # Add form to assign work to faculty...

    elif role == "Faculty":
        # Faculty Tab: Assign work to students
        student_tab = ttk.Frame(tabControl)
        tabControl.add(student_tab, text="Student Assignment")
        tabControl.pack(expand=1, fill="both")

        # Faculty functionality: Assign work to students
        assign_student_label = tk.Label(student_tab, text="Assign Work to Students")
        assign_student_label.pack()
        # Add form to assign work to students...

    elif role == "Student":
        # Student Tab: View assigned work
        student_tab = ttk.Frame(tabControl)
        tabControl.add(student_tab, text="Assigned Work")
        tabControl.pack(expand=1, fill="both")

        # Student functionality: View assignments
        view_assignments_label = tk.Label(student_tab, text="View Your Assignments")
        view_assignments_label.pack()
        # Add functionality to view student's assignments...

    dashboard.mainloop()

# Login Screen UI
root = tk.Tk()
root.title("Department Management System - Login")

# Username and Password Entry
tk.Label(root, text="Username").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# Login Button
login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

# Run the Login Window
root.mainloop()
