import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# Database connection function
def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # Use your MySQL password
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
        open_hod_dashboard(tabControl)
    elif role == "Faculty":
        open_faculty_dashboard(tabControl)
    elif role == "Student":
        open_student_dashboard(tabControl)

    tabControl.pack(expand=1, fill="both")
    dashboard.mainloop()

# HOD Dashboard Functionality: Assign work to faculty
def open_hod_dashboard(tabControl):
    hod_tab = ttk.Frame(tabControl)
    tabControl.add(hod_tab, text="Assign Work to Faculty")

    # Select Faculty (dropdown)
    tk.Label(hod_tab, text="Select Faculty").pack()
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT faculty_id, name FROM faculty")
    faculty_list = cursor.fetchall()
    faculty_combobox = ttk.Combobox(hod_tab, values=[faculty[1] for faculty in faculty_list])
    faculty_combobox.pack()
    cursor.close()
    connection.close()

    # Select Course (dropdown)
    tk.Label(hod_tab, text="Select Course").pack()
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT course_id, course_name FROM courses")
    courses = cursor.fetchall()
    course_combobox = ttk.Combobox(hod_tab, values=[course[1] for course in courses])
    course_combobox.pack()
    cursor.close()
    connection.close()

    # Assign Work Button
    assign_faculty_button = tk.Button(hod_tab, text="Assign Work", command=lambda: assign_work_to_faculty(faculty_combobox, course_combobox))
    assign_faculty_button.pack()

# Assign work to faculty (HOD)
def assign_work_to_faculty(faculty_combobox, course_combobox):
    faculty_id = faculty_combobox.get()
    course_id = course_combobox.get()
    
    connection = db_connection()
    cursor = connection.cursor()

    # Insert the assigned work to the faculty
    cursor.execute(
        "INSERT INTO faculty_work (faculty_id, course_id) VALUES (%s, %s)",
        (faculty_id, course_id)
    )
    connection.commit()
    messagebox.showinfo("Success", "Work assigned to faculty successfully!")
    cursor.close()
    connection.close()

# Faculty Dashboard Functionality: Assign work to students
def open_faculty_dashboard(tabControl):
    faculty_tab = ttk.Frame(tabControl)
    tabControl.add(faculty_tab, text="Assign Work to Student")

    # Title
    tk.Label(faculty_tab, text="Work Title").pack()
    entry_title = tk.Entry(faculty_tab)
    entry_title.pack()

    # Description
    tk.Label(faculty_tab, text="Description").pack()
    entry_description = tk.Entry(faculty_tab)
    entry_description.pack()

    # Select Student (dropdown)
    tk.Label(faculty_tab, text="Select Student").pack()
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    student_combobox = ttk.Combobox(faculty_tab, values=[student[1] for student in students])
    student_combobox.pack()
    cursor.close()
    connection.close()

    # Submission Date
    tk.Label(faculty_tab, text="Submission Date (YYYY-MM-DD)").pack()
    entry_submission_date = tk.Entry(faculty_tab)
    entry_submission_date.pack()

    # Assign Work Button
    assign_button = tk.Button(faculty_tab, text="Assign Work", command=lambda: assign_work_to_student(entry_title, entry_description, student_combobox, entry_submission_date))
    assign_button.pack()

# Assign work to student (Faculty)
def assign_work_to_student(entry_title, entry_description, student_combobox, entry_submission_date):
    title = entry_title.get()
    description = entry_description.get()
    student_id = student_combobox.get()
    faculty_id = 1  # You can dynamically fetch the logged-in faculty ID
    submission_date = entry_submission_date.get()

    connection = db_connection()
    cursor = connection.cursor()
    
    # Insert the assignment into the database
    cursor.execute(
        "INSERT INTO assignments (title, description, assigned_to, faculty_id, submission_date) "
        "VALUES (%s, %s, %s, %s, %s)",
        (title, description, student_id, faculty_id, submission_date)
    )
    connection.commit()
    messagebox.showinfo("Success", "Work assigned to student successfully!")
    cursor.close()
    connection.close()

# Student Dashboard Functionality: View Assignments
def open_student_dashboard(tabControl):
    student_tab = ttk.Frame(tabControl)
    tabControl.add(student_tab, text="Assigned Work")

    # View Assignments
    tk.Label(student_tab, text="View Your Assignments").pack()
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT title, description FROM assignments WHERE assigned_to=1")  # 1 is a placeholder for student ID
    assignments = cursor.fetchall()

    for assignment in assignments:
        tk.Label(student_tab, text=f"Title: {assignment[0]} - Description: {assignment[1]}").pack()

    cursor.close()
    connection.close()

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
