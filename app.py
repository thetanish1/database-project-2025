import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

# Database connection function with error handling
def db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="department_management"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to database: {err}")
        return None

# Initialize database with required tables, views, and procedures
def initialize_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS department_management")
        cursor.execute("USE department_management")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role ENUM('HOD', 'Faculty', 'Student') NOT NULL,
            associated_id INT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            roll_number VARCHAR(20) UNIQUE NOT NULL,
            department VARCHAR(50) NOT NULL,
            semester INT NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) UNIQUE NOT NULL,
            course_name VARCHAR(100) NOT NULL,
            credits INT NOT NULL,
            department VARCHAR(50) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_assignments (
            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
            faculty_id INT NOT NULL,
            course_id INT NOT NULL,
            assigned_date DATE NOT NULL,
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_assignments (
            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            faculty_id INT NOT NULL,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            assigned_date DATE NOT NULL,
            submission_date DATE NOT NULL,
            status ENUM('Pending', 'Submitted', 'Graded') DEFAULT 'Pending',
            grade VARCHAR(2),
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
        """)
        
        # Create views
        cursor.execute("""
        CREATE OR REPLACE VIEW faculty_course_view AS
        SELECT f.name AS faculty_name, c.course_name, c.course_code, fa.assigned_date
        FROM faculty_assignments fa
        JOIN faculty f ON fa.faculty_id = f.faculty_id
        JOIN courses c ON fa.course_id = c.course_id
        """)
        
        cursor.execute("""
        CREATE OR REPLACE VIEW student_assignment_view AS
        SELECT s.name AS student_name, a.title, a.description, 
               f.name AS faculty_name, c.course_name,
               a.assigned_date, a.submission_date, a.status, a.grade
        FROM student_assignments a
        JOIN students s ON a.student_id = s.student_id
        JOIN faculty f ON a.faculty_id = f.faculty_id
        JOIN courses c ON a.course_id = c.course_id
        """)
        
        # Create stored procedures
        cursor.execute("""
        CREATE PROCEDURE IF NOT EXISTS assign_faculty_to_course(
            IN p_faculty_id INT,
            IN p_course_id INT
        )
        BEGIN
            INSERT INTO faculty_assignments (faculty_id, course_id, assigned_date)
            VALUES (p_faculty_id, p_course_id, CURDATE());
        END
        """)
        
        cursor.execute("""
        CREATE PROCEDURE IF NOT EXISTS assign_student_work(
            IN p_title VARCHAR(100),
            IN p_description TEXT,
            IN p_faculty_id INT,
            IN p_student_id INT,
            IN p_course_id INT,
            IN p_submission_date DATE
        )
        BEGIN
            INSERT INTO student_assignments 
            (title, description, faculty_id, student_id, course_id, assigned_date, submission_date)
            VALUES (p_title, p_description, p_faculty_id, p_student_id, p_course_id, CURDATE(), p_submission_date);
        END
        """)
        
        # Create function
        cursor.execute("""
        CREATE FUNCTION IF NOT EXISTS count_assignments(
            p_student_id INT
        ) 
        RETURNS INT
        DETERMINISTIC
        BEGIN
            DECLARE assignment_count INT;
            SELECT COUNT(*) INTO assignment_count
            FROM student_assignments
            WHERE student_id = p_student_id;
            RETURN assignment_count;
        END
        """)
        
        # Create trigger
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS before_assignment_submission
        BEFORE UPDATE ON student_assignments
        FOR EACH ROW
        BEGIN
            IF NEW.status = 'Submitted' AND OLD.status != 'Submitted' THEN
                SET NEW.submission_date = CURDATE();
            END IF;
        END
        """)
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM faculty")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO faculty (name, department, email) VALUES
            ('Dr. Smith', 'Computer Science', 'smith@univ.edu'),
            ('Dr. Johnson', 'Mathematics', 'johnson@univ.edu'),
            ('Dr. Williams', 'Physics', 'williams@univ.edu')
            """)
            
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO students (name, roll_number, department, semester) VALUES
            ('Alice Brown', 'CS101', 'Computer Science', 3),
            ('Bob Davis', 'CS102', 'Computer Science', 3),
            ('Charlie Wilson', 'MATH101', 'Mathematics', 2)
            """)
            
        cursor.execute("SELECT COUNT(*) FROM courses")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO courses (course_code, course_name, credits, department) VALUES
            ('CS301', 'Database Systems', 4, 'Computer Science'),
            ('CS302', 'Algorithms', 3, 'Computer Science'),
            ('MATH201', 'Linear Algebra', 3, 'Mathematics')
            """)
            
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO users (username, password, role, associated_id) VALUES
            ('hod', 'hod123', 'HOD', 1),
            ('faculty1', 'faculty123', 'Faculty', 1),
            ('faculty2', 'faculty123', 'Faculty', 2),
            ('student1', 'student123', 'Student', 1),
            ('student2', 'student123', 'Student', 2)
            """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Initialization Error", f"Error initializing database: {err}")

# Login function with parameterized query to prevent SQL injection
def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and password are required!")
        return

    try:
        connection = db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
            
            if user:
                messagebox.showinfo("Login Success", "Login Successful!")
                root.destroy()
                open_dashboard(user['role'], user['associated_id'])
            else:
                messagebox.showerror("Login Failed", "Invalid credentials!")
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error during login: {err}")

# Open dashboard based on role
def open_dashboard(role, user_id):
    dashboard = tk.Tk()
    dashboard.title(f"{role} Dashboard")
    dashboard.geometry("800x600")

    # Tabs for different roles
    tab_control = ttk.Notebook(dashboard)

    if role == "HOD":
        hod_tab = ttk.Frame(tab_control)
        tab_control.add(hod_tab, text="Faculty Assignments")
        setup_hod_tab(hod_tab)
        
        report_tab = ttk.Frame(tab_control)
        tab_control.add(report_tab, text="Reports")
        setup_hod_report_tab(report_tab)
        
    elif role == "Faculty":
        faculty_tab = ttk.Frame(tab_control)
        tab_control.add(faculty_tab, text="Student Assignments")
        setup_faculty_tab(faculty_tab, user_id)
        
        grading_tab = ttk.Frame(tab_control)
        tab_control.add(grading_tab, text="Grade Assignments")
        setup_grading_tab(grading_tab, user_id)
        
    elif role == "Student":
        student_tab = ttk.Frame(tab_control)
        tab_control.add(student_tab, text="My Assignments")
        setup_student_tab(student_tab, user_id)
        
        submit_tab = ttk.Frame(tab_control)
        tab_control.add(submit_tab, text="Submit Work")
        setup_submit_tab(submit_tab, user_id)

    tab_control.pack(expand=1, fill="both")
    dashboard.mainloop()

# HOD Tab: Assign courses to faculty
def setup_hod_tab(tab):
    # Faculty selection
    tk.Label(tab, text="Select Faculty:").pack(pady=5)
    faculty_combobox = ttk.Combobox(tab, state="readonly")
    faculty_combobox.pack(pady=5)
    
    # Course selection
    tk.Label(tab, text="Select Course:").pack(pady=5)
    course_combobox = ttk.Combobox(tab, state="readonly")
    course_combobox.pack(pady=5)
    
    # Load data
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Get faculty
        cursor.execute("SELECT faculty_id, name FROM faculty")
        faculty_list = [(row[0], row[1]) for row in cursor.fetchall()]
        faculty_combobox['values'] = [f"{fid} - {name}" for fid, name in faculty_list]
        
        # Get courses
        cursor.execute("SELECT course_id, course_code, course_name FROM courses")
        course_list = [(row[0], f"{row[1]} - {row[2]}") for row in cursor.fetchall()]
        course_combobox['values'] = [name for _, name in course_list]
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading data: {err}")
    
    # Assign button
    assign_btn = tk.Button(tab, text="Assign Course", 
                          command=lambda: assign_course_to_faculty(faculty_combobox, course_combobox))
    assign_btn.pack(pady=10)
    
    # Display current assignments using view
    tk.Label(tab, text="Current Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    assignments_tree = ttk.Treeview(tab, columns=('Faculty', 'Course', 'Assigned Date'), show='headings')
    assignments_tree.heading('Faculty', text='Faculty')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Assigned Date', text='Assigned Date')
    assignments_tree.pack(fill='both', expand=True)
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faculty_course_view")
        for row in cursor.fetchall():
            assignments_tree.insert('', 'end', values=(row[0], row[1], row[3]))
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")

# Improved version with validation
def assign_course_to_faculty(faculty_cb, course_cb):
    try:
        faculty_selection = faculty_cb.get()
        course_selection = course_cb.get()
        
        if not faculty_selection or not course_selection:
            raise ValueError("Please select both faculty and course")
        
        # Get IDs safely
        faculty_parts = faculty_selection.split(" - ")
        course_parts = course_selection.split(" - ")
        
        if len(faculty_parts) < 1 or len(course_parts) < 1:
            raise ValueError("Invalid selection format")
            
        faculty_id = int(faculty_parts[0])
        course_id = int(course_parts[0])
        
        # Rest of the database code...
        
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
# HOD Report Tab
def setup_hod_report_tab(tab):
    # Department selection
    tk.Label(tab, text="Select Department:").pack(pady=5)
    dept_combobox = ttk.Combobox(tab, values=['Computer Science', 'Mathematics', 'Physics'])
    dept_combobox.pack(pady=5)
    
    # Generate report button
    report_btn = tk.Button(tab, text="Generate Report", 
                          command=lambda: generate_department_report(dept_combobox, report_tree))
    report_btn.pack(pady=10)
    
    # Report display
    report_tree = ttk.Treeview(tab, columns=('Faculty', 'Courses', 'Students'), show='headings')
    report_tree.heading('Faculty', text='Faculty')
    report_tree.heading('Courses', text='Courses Assigned')
    report_tree.heading('Students', text='Students Enrolled')
    report_tree.pack(fill='both', expand=True)

def generate_department_report(dept_cb, tree):
    department = dept_cb.get()
    if not department:
        messagebox.showerror("Error", "Please select a department")
        return
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Get faculty count and courses per faculty
        cursor.execute("""
        SELECT f.name, COUNT(DISTINCT fa.course_id), 
               (SELECT COUNT(DISTINCT s.student_id) 
                FROM students s
                JOIN student_assignments sa ON s.student_id = sa.student_id
                JOIN courses c ON sa.course_id = c.course_id
                WHERE c.department = %s AND fa.faculty_id = sa.faculty_id)
        FROM faculty f
        LEFT JOIN faculty_assignments fa ON f.faculty_id = fa.faculty_id
        LEFT JOIN courses c ON fa.course_id = c.course_id
        WHERE f.department = %s
        GROUP BY f.faculty_id
        """, (department, department))
        
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error generating report: {err}")

# Faculty Tab: Assign work to students
def setup_faculty_tab(tab, faculty_id):
    # Student selection
    tk.Label(tab, text="Select Student:").pack(pady=5)
    student_combobox = ttk.Combobox(tab, state="readonly")
    student_combobox.pack(pady=5)
    
    # Course selection
    tk.Label(tab, text="Select Course:").pack(pady=5)
    course_combobox = ttk.Combobox(tab, state="readonly")
    course_combobox.pack(pady=5)
    
    # Assignment details
    tk.Label(tab, text="Assignment Title:").pack(pady=5)
    title_entry = tk.Entry(tab)
    title_entry.pack(pady=5)
    
    tk.Label(tab, text="Description:").pack(pady=5)
    desc_text = tk.Text(tab, height=5, width=50)
    desc_text.pack(pady=5)
    
    tk.Label(tab, text="Submission Date (YYYY-MM-DD):").pack(pady=5)
    sub_date_entry = tk.Entry(tab)
    sub_date_entry.pack(pady=5)
    
    # Load data
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Get students
        cursor.execute("SELECT student_id, name FROM students")
        student_list = [(row[0], row[1]) for row in cursor.fetchall()]
        student_combobox['values'] = [f"{sid} - {name}" for sid, name in student_list]
        
        # Get courses assigned to this faculty
        cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name 
        FROM faculty_assignments fa
        JOIN courses c ON fa.course_id = c.course_id
        WHERE fa.faculty_id = %s
        """, (faculty_id,))
        course_list = [(row[0], f"{row[1]} - {row[2]}") for row in cursor.fetchall()]
        course_combobox['values'] = [name for _, name in course_list]
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading data: {err}")
    
    # Assign button
    assign_btn = tk.Button(tab, text="Create Assignment", 
                          command=lambda: create_student_assignment(
                              faculty_id, student_combobox, course_combobox,
                              title_entry, desc_text, sub_date_entry
                          ))
    assign_btn.pack(pady=10)
    
    # Display current assignments
    tk.Label(tab, text="Current Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    assignments_tree = ttk.Treeview(tab, columns=('Student', 'Course', 'Title', 'Due Date', 'Status'), show='headings')
    assignments_tree.heading('Student', text='Student')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Title', text='Title')
    assignments_tree.heading('Due Date', text='Due Date')
    assignments_tree.heading('Status', text='Status')
    assignments_tree.pack(fill='both', expand=True)
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.name, c.course_name, a.title, a.submission_date, a.status
        FROM student_assignments a
        JOIN students s ON a.student_id = s.student_id
        JOIN courses c ON a.course_id = c.course_id
        WHERE a.faculty_id = %s
        """, (faculty_id,))
        
        for row in cursor.fetchall():
            assignments_tree.insert('', 'end', values=row)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")

def setup_student_tab(tab, student_id):
    # Display assignments
    tk.Label(tab, text="Your Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    
    assignments_tree = ttk.Treeview(tab, columns=('Course', 'Title', 'Due Date', 'Status', 'Grade'), show='headings')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Title', text='Title')
    assignments_tree.heading('Due Date', text='Due Date')
    assignments_tree.heading('Status', text='Status')
    assignments_tree.heading('Grade', text='Grade')
    assignments_tree.pack(fill='both', expand=True)
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Fixed query using student_id
        cursor.execute("""
        SELECT course_name, title, submission_date, status, grade
        FROM student_assignment_view
        WHERE student_id = %s
        """, (student_id,))
        
        for row in cursor.fetchall():
            assignments_tree.insert('', 'end', values=row)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")

# Faculty Grading Tab
def setup_grading_tab(tab, faculty_id):
    # Assignment selection
    tk.Label(tab, text="Select Assignment to Grade:").pack(pady=5)
    assignment_combobox = ttk.Combobox(tab, state="readonly")
    assignment_combobox.pack(pady=5)
    
    # Grade entry
    tk.Label(tab, text="Grade (A-F):").pack(pady=5)
    grade_entry = tk.Entry(tab)
    grade_entry.pack(pady=5)
    
    # Load assignments
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT a.assignment_id, s.name, a.title, a.status
        FROM student_assignments a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.faculty_id = %s AND a.status = 'Submitted'
        """, (faculty_id,))
        
        assignments = [(row[0], f"{row[1]} - {row[2]} ({'Submitted' if row[3] == 'Submitted' else 'Graded'})") 
                      for row in cursor.fetchall()]
        assignment_combobox['values'] = [name for _, name in assignments]
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")
    
    # Grade button
    grade_btn = tk.Button(tab, text="Submit Grade", 
                         command=lambda: submit_grade(assignment_combobox, grade_entry))
    grade_btn.pack(pady=10)
    
    # Display graded assignments
    tk.Label(tab, text="Graded Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    graded_tree = ttk.Treeview(tab, columns=('Student', 'Assignment', 'Grade'), show='headings')
    graded_tree.heading('Student', text='Student')
    graded_tree.heading('Assignment', text='Assignment')
    graded_tree.heading('Grade', text='Grade')
    graded_tree.pack(fill='both', expand=True)
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.name, a.title, a.grade
        FROM student_assignments a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.faculty_id = %s AND a.status = 'Graded'
        """, (faculty_id,))
        
        for row in cursor.fetchall():
            graded_tree.insert('', 'end', values=row)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading graded assignments: {err}")

def submit_grade(assignment_cb, grade_entry):
    assignment_selection = assignment_cb.get()
    grade = grade_entry.get().upper()
    
    if not assignment_selection or not grade:
        messagebox.showerror("Error", "Please select an assignment and enter a grade")
        return
    
    if grade not in ['A', 'B', 'C', 'D', 'F']:
        messagebox.showerror("Error", "Grade must be A, B, C, D, or F")
        return
    
    assignment_id = assignment_selection.split(" - ")[0]
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE student_assignments 
        SET grade = %s, status = 'Graded'
        WHERE assignment_id = %s
        """, (grade, assignment_id))
        conn.commit()
        
        messagebox.showinfo("Success", "Grade submitted successfully!")
        grade_entry.delete(0, tk.END)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error submitting grade: {err}")

# Student Tab: View assignments
def setup_student_tab(tab, student_id):
    # Display assignments
    tk.Label(tab, text="Your Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    
    assignments_tree = ttk.Treeview(tab, columns=('Course', 'Title', 'Due Date', 'Status', 'Grade'), show='headings')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Title', text='Title')
    assignments_tree.heading('Due Date', text='Due Date')
    assignments_tree.heading('Status', text='Status')
    assignments_tree.heading('Grade', text='Grade')
    assignments_tree.pack(fill='both', expand=True)
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Fixed query using proper column name
        cursor.execute("""
        SELECT course_name, title, submission_date, status, grade
        FROM student_assignment_view
        WHERE student_id = %s
        """, (student_id,))
        
        for row in cursor.fetchall():
            assignments_tree.insert('', 'end', values=row)
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")

# Student Submit Tab
def setup_submit_tab(tab, student_id):
    # Assignment selection
    tk.Label(tab, text="Select Assignment to Submit:").pack(pady=5)
    assignment_combobox = ttk.Combobox(tab, state="readonly")
    assignment_combobox.pack(pady=5)
    
    # Load pending assignments
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT a.assignment_id, c.course_name, a.title
        FROM student_assignments a
        JOIN courses c ON a.course_id = c.course_id
        WHERE a.student_id = %s AND a.status = 'Pending'
        """, (student_id,))
        
        assignments = [(row[0], f"{row[1]} - {row[2]}") for row in cursor.fetchall()]
        assignment_combobox['values'] = [name for _, name in assignments]
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error loading assignments: {err}")
    
    # Submit button
    submit_btn = tk.Button(tab, text="Mark as Submitted", 
                          command=lambda: submit_assignment(assignment_combobox))
    submit_btn.pack(pady=10)

def submit_assignment(assignment_cb):
    assignment_selection = assignment_cb.get()
    if not assignment_selection:
        messagebox.showerror("Error", "Please select an assignment")
        return
    
    assignment_id = assignment_selection.split(" - ")[0]
    
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # This will trigger our before_assignment_submission trigger
        cursor.execute("""
        UPDATE student_assignments 
        SET status = 'Submitted'
        WHERE assignment_id = %s
        """, (assignment_id,))
        conn.commit()
        
        messagebox.showinfo("Success", "Assignment submitted successfully!")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error submitting assignment: {err}")

# Main application
if __name__ == "__main__":
    # Initialize database
    initialize_database()
    
    # Login Screen UI
    root = tk.Tk()
    root.title("Department Management System - Login")
    root.geometry("400x300")
    
    # Center the window
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Login frame
    login_frame = tk.Frame(root, padx=20, pady=20)
    login_frame.pack(expand=True)
    
    # Username and Password Entry
    tk.Label(login_frame, text="Username").pack()
    entry_username = tk.Entry(login_frame)
    entry_username.pack(pady=5)
    
    tk.Label(login_frame, text="Password").pack()
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.pack(pady=5)
    
    # Login Button
    login_button = tk.Button(login_frame, text="Login", command=login)
    login_button.pack(pady=20)
    
    # Run the Login Window
    root.mainloop()