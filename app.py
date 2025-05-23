import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
from tkinter import simpledialog


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
    dashboard.title(f"Department Management System - {role} Dashboard")
    dashboard.geometry("1000x700")

    # Create tab control
    tab_control = ttk.Notebook(dashboard)

    if role == "HOD":
        # Create tabs
        hod_tab = ttk.Frame(tab_control)
        report_tab = ttk.Frame(tab_control)
        
        # Add tabs to notebook
        tab_control.add(hod_tab, text="Faculty Assignments")
        tab_control.add(report_tab, text="Reports")
        
        # Setup tabs
        setup_hod_tab(hod_tab, dashboard)
        setup_hod_report_tab(report_tab)

    elif role == "Faculty":
        # Create tabs
        faculty_tab = ttk.Frame(tab_control)
        grading_tab = ttk.Frame(tab_control)
        
        # Add tabs to notebook
        tab_control.add(faculty_tab, text="Student Assignments")
        tab_control.add(grading_tab, text="Grade Assignments")
        
        # Setup tabs with dashboard window reference
        setup_faculty_tab(faculty_tab, dashboard, user_id)
        setup_grading_tab(grading_tab, user_id)

    elif role == "Student":
        # Create tabs
        student_tab = ttk.Frame(tab_control)
        submit_tab = ttk.Frame(tab_control)
        
        # Add tabs to notebook
        tab_control.add(student_tab, text="My Assignments")
        tab_control.add(submit_tab, text="Submit Work")
        
        # Setup tabs
        setup_student_tab(student_tab, user_id)
        setup_submit_tab(submit_tab, user_id)

    # Pack the notebook
    tab_control.pack(expand=True, fill='both', padx=10, pady=10)
    
    # Center the window on screen
    window_width = 1000
    window_height = 700
    screen_width = dashboard.winfo_screenwidth()
    screen_height = dashboard.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    dashboard.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    dashboard.mainloop()

# HOD Tab: Assign courses to faculty
def setup_hod_tab(tab, dashboard_window):
    # Add logout button at the top
    logout_btn = tk.Button(tab, text="Logout", command=lambda: logout(dashboard_window))
    logout_btn.pack(anchor='ne', padx=10, pady=5)
    
    # Faculty selection
    tk.Label(tab, text="Select Faculty:").pack(pady=5)
    faculty_combobox = ttk.Combobox(tab, state="readonly")
    faculty_combobox.pack(pady=5)
    
    # Course selection
    tk.Label(tab, text="Select Course:").pack(pady=5)
    course_combobox = ttk.Combobox(tab, state="readonly")
    course_combobox.pack(pady=5)
    
    # Assignment selection for update/remove
    tk.Label(tab, text="Select Assignment to Update/Remove:").pack(pady=5)
    assignment_combobox = ttk.Combobox(tab, state="readonly")
    assignment_combobox.pack(pady=5)
    
    # Load data with numbered faculty names
    def load_data():
        try:
            conn = db_connection()
            cursor = conn.cursor()
            
            # Get faculty with numbering
            cursor.execute("SELECT faculty_id, name FROM faculty ORDER BY name")
            faculty_list = [(row[0], row[1]) for row in cursor.fetchall()]
            numbered_faculty = [f"{idx+1}. {name} (ID: {fid})" for idx, (fid, name) in enumerate(faculty_list)]
            faculty_combobox['values'] = numbered_faculty
            
            # Get courses
            cursor.execute("SELECT course_id, course_code, course_name FROM courses ORDER BY course_code")
            course_list = [(row[0], f"{row[1]} - {row[2]}") for row in cursor.fetchall()]
            course_combobox['values'] = [name for _, name in course_list]
            
            # Get current assignments for combobox
            cursor.execute("""
            SELECT fa.assignment_id, f.name, c.course_code 
            FROM faculty_assignments fa
            JOIN faculty f ON fa.faculty_id = f.faculty_id
            JOIN courses c ON fa.course_id = c.course_id
            ORDER BY f.name, c.course_code
            """)
            assignments = [f"{idx+1}. {row[1]} -> {row[2]} (ID: {row[0]})" 
                         for idx, row in enumerate(cursor.fetchall())]
            assignment_combobox['values'] = assignments
            
            cursor.close()
            conn.close()
            refresh_assignments()  # Refresh the treeview
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading data: {err}")
    
    # Button frame
    button_frame = tk.Frame(tab)
    button_frame.pack(pady=10)
    
    # Assign button
    assign_btn = tk.Button(button_frame, text="Assign Course", 
                         command=lambda: assign_course_to_faculty(faculty_combobox, course_combobox, load_data))
    assign_btn.grid(row=0, column=0, padx=5)
    
    # Update button
    update_btn = tk.Button(button_frame, text="Update Assignment", 
                         command=lambda: update_assignment(assignment_combobox, faculty_combobox, course_combobox, load_data))
    update_btn.grid(row=0, column=1, padx=5)
    
    # Remove button
    remove_btn = tk.Button(button_frame, text="Remove Assignment", 
                         command=lambda: remove_assignment(assignment_combobox, load_data))
    remove_btn.grid(row=0, column=2, padx=5)
    
    # Display current assignments
    tk.Label(tab, text="Current Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    assignments_tree = ttk.Treeview(tab, columns=('#', 'Faculty', 'Course', 'Assigned Date'), show='headings')
    assignments_tree.heading('#', text='#')
    assignments_tree.heading('Faculty', text='Faculty')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Assigned Date', text='Assigned Date')
    assignments_tree.column('#', width=50, anchor='center')
    assignments_tree.pack(fill='both', expand=True)
    
    def refresh_assignments():
        try:
            for item in assignments_tree.get_children():
                assignments_tree.delete(item)
            
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY f.name, c.course_code) as row_num,
                   f.name, c.course_name, fa.assigned_date
            FROM faculty_assignments fa
            JOIN faculty f ON fa.faculty_id = f.faculty_id
            JOIN courses c ON fa.course_id = c.course_id
            """)
            
            for idx, row in enumerate(cursor.fetchall()):
                assignments_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3]))
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading assignments: {err}")
    
    # Initial load
    load_data()

def assign_course_to_faculty(faculty_cb, course_cb, callback):
    try:
        faculty_selection = faculty_cb.get()
        course_selection = course_cb.get()
        
        if not faculty_selection or not course_selection:
            raise ValueError("Please select both faculty and course")
        
        # Extract faculty ID from the numbered string
        faculty_id = int(faculty_selection.split("ID: ")[1].rstrip(")"))
        
        # Get course ID
        course_code = course_selection.split(" - ")[0]
        
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Find course ID
            cursor.execute("SELECT course_id FROM courses WHERE course_code = %s", (course_code,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Selected course not found in database")
            course_id = result[0]
            
            # Check for existing assignment
            cursor.execute("""
            SELECT COUNT(*) FROM faculty_assignments 
            WHERE faculty_id = %s AND course_id = %s
            """, (faculty_id, course_id))
            if cursor.fetchone()[0] > 0:
                raise ValueError("This faculty is already assigned to this course")
            
            # Assign course
            cursor.callproc("assign_faculty_to_course", (faculty_id, course_id))
            conn.commit()
            messagebox.showinfo("Success", "Course assigned successfully!")
            
            cursor.close()
            conn.close()
            callback()  # Refresh all data
            
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error assigning course: {err}")

def remove_assignment(assignment_cb, callback):
    try:
        assignment_selection = assignment_cb.get()
        if not assignment_selection:
            raise ValueError("Please select an assignment to remove")
        
        # Extract assignment ID from the numbered string
        assignment_id = int(assignment_selection.split("ID: ")[1].rstrip(")"))
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove this assignment?"):
            return
        
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Delete assignment
            cursor.execute("DELETE FROM faculty_assignments WHERE assignment_id = %s", (assignment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Assignment removed successfully!")
            
            cursor.close()
            conn.close()
            callback()  # Refresh all data
            
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error removing assignment: {err}")

def logout(dashboard_window):
    dashboard_window.destroy()
    show_login_window()

def show_login_window():
    # Login Screen UI
    login_window = tk.Tk()
    login_window.title("Department Management System - Login")
    login_window.geometry("400x300")
    
    # Center the window
    window_width = 400
    window_height = 300
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Login frame
    login_frame = tk.Frame(login_window, padx=20, pady=20)
    login_frame.pack(expand=True)
    
    # Username and Password Entry
    tk.Label(login_frame, text="Username").pack()
    entry_username = tk.Entry(login_frame)
    entry_username.pack(pady=5)
    
    tk.Label(login_frame, text="Password").pack()
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.pack(pady=5)
    
    # Login Button
    login_button = tk.Button(login_frame, text="Login", command=lambda: login(entry_username, entry_password, login_window))
    login_button.pack(pady=20)
    
    login_window.mainloop()

def login(entry_username, entry_password, login_window):
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
                login_window.destroy()  # Close login window
                open_dashboard(user['role'], user['associated_id'])
            else:
                messagebox.showerror("Login Failed", "Invalid credentials!")
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error during login: {err}")

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
def setup_faculty_tab(tab, dashboard_window, faculty_id):
    # Add logout button
    logout_btn = tk.Button(tab, text="Logout", bg='#ff6b6b', fg='white',
                         command=lambda: logout(dashboard_window))
    logout_btn.pack(anchor='ne', padx=10, pady=5)

    # Main container frame
    main_frame = ttk.Frame(tab)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Left frame for assignment creation
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    # Right frame for assignment management
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    # Assignment Creation Section
    ttk.Label(left_frame, text="Create New Assignment", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Student selection with numbering
    ttk.Label(left_frame, text="Select Student:").pack(pady=5)
    student_combobox = ttk.Combobox(left_frame, state="readonly", width=30)
    student_combobox.pack(pady=5)

    # Course selection
    ttk.Label(left_frame, text="Select Course:").pack(pady=5)
    course_combobox = ttk.Combobox(left_frame, state="readonly", width=30)
    course_combobox.pack(pady=5)

    # Assignment details
    ttk.Label(left_frame, text="Assignment Title:").pack(pady=5)
    title_entry = ttk.Entry(left_frame, width=30)
    title_entry.pack(pady=5)

    ttk.Label(left_frame, text="Description:").pack(pady=5)
    desc_text = tk.Text(left_frame, height=5, width=30)
    desc_text.pack(pady=5)

    ttk.Label(left_frame, text="Submission Date (YYYY-MM-DD):").pack(pady=5)
    sub_date_entry = ttk.Entry(left_frame, width=30)
    sub_date_entry.pack(pady=5)

    # Assignment Management Section
    ttk.Label(right_frame, text="Manage Assignments", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Assignment selection for removal
    ttk.Label(right_frame, text="Select Assignment to Remove:").pack(pady=5)
    remove_assignment_combobox = ttk.Combobox(right_frame, state="readonly", width=30)
    remove_assignment_combobox.pack(pady=5)

    # Button frame
    button_frame = ttk.Frame(left_frame)
    button_frame.pack(pady=10)

    # Create assignment button - FIXED VERSION
    create_btn = ttk.Button(button_frame, text="Create Assignment",
                      command=lambda: create_student_assignment(
                          faculty_id, 
                          student_combobox, 
                          course_combobox,
                          title_entry, 
                          desc_text, 
                          sub_date_entry,
                          load_data))  # Now passing 7 arguments correctly
    create_btn.grid(row=0, column=0, padx=5)

    # Remove assignment button
    remove_btn = ttk.Button(right_frame, text="Remove Assignment",
                          command=lambda: remove_student_assignment(
                              remove_assignment_combobox, load_data))
    remove_btn.pack(pady=10)

    # Display current assignments
    ttk.Label(right_frame, text="Current Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    
    # Treeview with scrollbar
    tree_frame = ttk.Frame(right_frame)
    tree_frame.pack(fill='both', expand=True)
    
    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side='right', fill='y')
    
    assignments_tree = ttk.Treeview(tree_frame, 
                                  columns=('#', 'Student', 'Course', 'Title', 'Due Date', 'Status'), 
                                  show='headings',
                                  yscrollcommand=tree_scroll.set)
    assignments_tree.pack(fill='both', expand=True)
    tree_scroll.config(command=assignments_tree.yview)
    
    # Configure columns
    assignments_tree.heading('#', text='#')
    assignments_tree.heading('Student', text='Student')
    assignments_tree.heading('Course', text='Course')
    assignments_tree.heading('Title', text='Title')
    assignments_tree.heading('Due Date', text='Due Date')
    assignments_tree.heading('Status', text='Status')
    
    assignments_tree.column('#', width=40, anchor='center')
    assignments_tree.column('Student', width=120)
    assignments_tree.column('Course', width=120)
    assignments_tree.column('Title', width=150)
    assignments_tree.column('Due Date', width=100, anchor='center')
    assignments_tree.column('Status', width=80, anchor='center')

    def load_data():
        try:
            conn = db_connection()
            cursor = conn.cursor()
            
            # Get students with numbering
            cursor.execute("SELECT student_id, name FROM students ORDER BY name")
            students = [(row[0], row[1]) for row in cursor.fetchall()]
            numbered_students = [f"{idx+1}. {name} (ID: {sid})" for idx, (sid, name) in enumerate(students)]
            student_combobox['values'] = numbered_students
            student_combobox.set('')
            
            # Get courses assigned to this faculty
            cursor.execute("""
            SELECT c.course_id, c.course_code, c.course_name 
            FROM faculty_assignments fa
            JOIN courses c ON fa.course_id = c.course_id
            WHERE fa.faculty_id = %s
            ORDER BY c.course_code
            """, (faculty_id,))
            course_list = [(row[0], f"{row[1]} - {row[2]}") for row in cursor.fetchall()]
            course_combobox['values'] = [name for _, name in course_list]
            course_combobox.set('')
            
            # Get current assignments for removal combobox
            cursor.execute("""
            SELECT a.assignment_id, s.name, c.course_code, a.title
            FROM student_assignments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.faculty_id = %s
            ORDER BY s.name, a.assigned_date DESC
            """, (faculty_id,))
            assignments = [f"{idx+1}. {row[1]} - {row[2]} ({row[3]}) (ID: {row[0]})" 
                         for idx, row in enumerate(cursor.fetchall())]
            remove_assignment_combobox['values'] = assignments
            remove_assignment_combobox.set('')
            
            refresh_assignments()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading data: {err}")

    def refresh_assignments():
        try:
            # Clear existing data
            for item in assignments_tree.get_children():
                assignments_tree.delete(item)
            
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY s.name, a.submission_date) as row_num,
                   s.name, c.course_name, a.title, 
                   DATE_FORMAT(a.submission_date, '%Y-%m-%d'), 
                   a.status
            FROM student_assignments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.faculty_id = %s
            """, (faculty_id,))
            
            # Insert data with alternating colors
            for i, row in enumerate(cursor.fetchall()):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                assignments_tree.insert('', 'end', values=row, tags=(tag,))
            
            # Configure tags for alternating colors
            assignments_tree.tag_configure('evenrow', background='#f5f5f5')
            assignments_tree.tag_configure('oddrow', background='white')
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading assignments: {err}")

    # Initial data load
    load_data()

def remove_student_assignment(assignment_cb, callback):
    try:
        assignment_selection = assignment_cb.get()
        if not assignment_selection:
            raise ValueError("Please select an assignment to remove")
        
        # Extract assignment ID
        assignment_id = int(assignment_selection.split("ID: ")[1].rstrip(")"))
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove this assignment?"):
            return
        
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student_assignments WHERE assignment_id = %s", (assignment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Assignment removed successfully!")
            callback()  # Refresh all data
            cursor.close()
            conn.close()
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error removing assignment: {err}")
        

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
    # Add logout button
    logout_btn = tk.Button(tab, text="Logout", bg='#ff6b6b', fg='white',
                         command=lambda: logout(tab.winfo_toplevel()))
    logout_btn.pack(anchor='ne', padx=10, pady=5)

    # Main container frame
    main_frame = ttk.Frame(tab)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Left frame for grading
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

    # Right frame for grade management
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    # Grading Section
    ttk.Label(left_frame, text="Grade Assignments", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Assignment selection with numbering
    ttk.Label(left_frame, text="Select Assignment to Grade:").pack(pady=5)
    assignment_combobox = ttk.Combobox(left_frame, state="readonly", width=30)
    assignment_combobox.pack(pady=5)

    # Grade entry
    ttk.Label(left_frame, text="Grade (A-F):").pack(pady=5)
    grade_entry = ttk.Entry(left_frame, width=30)
    grade_entry.pack(pady=5)

    # Grade Management Section
    ttk.Label(right_frame, text="Manage Grades", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Assignment selection for grade removal
    ttk.Label(right_frame, text="Select Assignment to Remove Grade:").pack(pady=5)
    remove_grade_combobox = ttk.Combobox(right_frame, state="readonly", width=30)
    remove_grade_combobox.pack(pady=5)

    # Button frame
    button_frame = ttk.Frame(left_frame)
    button_frame.pack(pady=10)

    # Grade button
    grade_btn = ttk.Button(button_frame, text="Submit Grade",
                         command=lambda: submit_grade(
                             assignment_combobox, grade_entry, load_data))
    grade_btn.grid(row=0, column=0, padx=5)

    # Remove grade button
    remove_grade_btn = ttk.Button(right_frame, text="Remove Grade",
                                command=lambda: remove_grade(
                                    remove_grade_combobox, load_data))
    remove_grade_btn.pack(pady=10)

    # Display graded assignments
    ttk.Label(right_frame, text="Graded Assignments:", font=('Arial', 10, 'bold')).pack(pady=10)
    
    # Treeview with scrollbar
    tree_frame = ttk.Frame(right_frame)
    tree_frame.pack(fill='both', expand=True)
    
    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side='right', fill='y')
    
    graded_tree = ttk.Treeview(tree_frame, 
                             columns=('#', 'Student', 'Course', 'Assignment', 'Grade'), 
                             show='headings',
                             yscrollcommand=tree_scroll.set)
    graded_tree.pack(fill='both', expand=True)
    tree_scroll.config(command=graded_tree.yview)
    
    # Configure columns
    graded_tree.heading('#', text='#')
    graded_tree.heading('Student', text='Student')
    graded_tree.heading('Course', text='Course')
    graded_tree.heading('Assignment', text='Assignment')
    graded_tree.heading('Grade', text='Grade')
    
    graded_tree.column('#', width=40, anchor='center')
    graded_tree.column('Student', width=120)
    graded_tree.column('Course', width=120)
    graded_tree.column('Assignment', width=150)
    graded_tree.column('Grade', width=60, anchor='center')

    def load_data():
        try:
            conn = db_connection()
            cursor = conn.cursor()
            
            # Get assignments ready for grading (submitted but not graded)
            cursor.execute("""
            SELECT a.assignment_id, s.name, c.course_name, a.title
            FROM student_assignments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.faculty_id = %s AND a.status = 'Submitted'
            ORDER BY s.name, a.submission_date
            """, (faculty_id,))
            
            assignments = [f"{idx+1}. {row[1]} - {row[2]} ({row[3]}) (ID: {row[0]})" 
                         for idx, row in enumerate(cursor.fetchall())]
            assignment_combobox['values'] = assignments
            assignment_combobox.set('')
            
            # Get graded assignments for removal combobox
            cursor.execute("""
            SELECT a.assignment_id, s.name, c.course_name, a.title, a.grade
            FROM student_assignments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.faculty_id = %s AND a.status = 'Graded'
            ORDER BY s.name, a.submission_date
            """, (faculty_id,))
            
            graded_assignments = [f"{idx+1}. {row[1]} - {row[2]} ({row[3]}) - {row[4]} (ID: {row[0]})" 
                               for idx, row in enumerate(cursor.fetchall())]
            remove_grade_combobox['values'] = graded_assignments
            remove_grade_combobox.set('')
            
            refresh_graded_assignments()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading data: {err}")

    def refresh_graded_assignments():
        try:
            # Clear existing data
            for item in graded_tree.get_children():
                graded_tree.delete(item)
            
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY s.name, a.submission_date) as row_num,
                   s.name, c.course_name, a.title, a.grade
            FROM student_assignments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.faculty_id = %s AND a.status = 'Graded'
            """, (faculty_id,))
            
            # Insert data with alternating colors
            for i, row in enumerate(cursor.fetchall()):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                graded_tree.insert('', 'end', values=row, tags=(tag,))
            
            # Configure tags for alternating colors
            graded_tree.tag_configure('evenrow', background='#f5f5f5')
            graded_tree.tag_configure('oddrow', background='white')
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading graded assignments: {err}")

    def submit_grade(assignment_cb, grade_entry, callback):
        try:
            assignment_selection = assignment_cb.get()
            grade = grade_entry.get().upper()
            
            if not assignment_selection or not grade:
                raise ValueError("Please select an assignment and enter a grade")
            
            if grade not in ['A', 'B', 'C', 'D', 'F']:
                raise ValueError("Grade must be A, B, C, D, or F")
            
            # Extract assignment ID from the formatted string
            assignment_id = int(assignment_selection.split("ID: ")[1].rstrip(")"))
            
            conn = db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE student_assignments 
                SET grade = %s, status = 'Graded'
                WHERE assignment_id = %s
                """, (grade, assignment_id))
                conn.commit()
                messagebox.showinfo("Success", "Grade submitted successfully!")
                grade_entry.delete(0, tk.END)
                callback()
                cursor.close()
                conn.close()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error submitting grade: {err}")

    def remove_grade(assignment_cb, callback):
        try:
            assignment_selection = assignment_cb.get()
            if not assignment_selection:
                raise ValueError("Please select an assignment to remove grade")
            
            # Extract assignment ID from the formatted string
            assignment_id = int(assignment_selection.split("ID: ")[1].rstrip(")"))
            
            # Confirm removal
            if not messagebox.askyesno("Confirm", "Are you sure you want to remove this grade?"):
                return
            
            conn = db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE student_assignments 
                SET grade = NULL, status = 'Submitted'
                WHERE assignment_id = %s
                """, (assignment_id,))
                conn.commit()
                messagebox.showinfo("Success", "Grade removed successfully!")
                callback()
                cursor.close()
                conn.close()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error removing grade: {err}")

    # Initial data load
    load_data()
    
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

def create_student_assignment(faculty_id, student_cb, course_cb, title_entry, desc_text, sub_date_entry, callback):
    try:
        student_selection = student_cb.get()
        course_selection = course_cb.get()
        title = title_entry.get()
        description = desc_text.get("1.0", tk.END).strip()
        sub_date = sub_date_entry.get()
        
        if not all([student_selection, course_selection, title, description, sub_date]):
            raise ValueError("All fields are required!")
        
        # Validate date format
        try:
            datetime.strptime(sub_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Get student ID from the formatted string (e.g., "1. Alice Brown (ID: 1)")
        student_id = int(student_selection.split("ID: ")[1].rstrip(")"))
        
        # Get course ID by looking up the course code
        course_code = course_selection.split(" - ")[0]
        
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Find course ID
            cursor.execute("SELECT course_id FROM courses WHERE course_code = %s", (course_code,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Selected course not found in database")
            course_id = result[0]
            
            # Call stored procedure
            cursor.callproc("assign_student_work", 
                          (title, description, faculty_id, student_id, course_id, sub_date))
            conn.commit()
            messagebox.showinfo("Success", "Assignment created successfully!")
            
            # Clear form
            title_entry.delete(0, tk.END)
            desc_text.delete("1.0", tk.END)
            sub_date_entry.delete(0, tk.END)
            
            # Refresh data using callback
            callback()
            
            cursor.close()
            conn.close()
        
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error creating assignment: {err}")

    try:
        student_selection = student_cb.get()
        course_selection = course_cb.get()
        title = title_entry.get()
        description = desc_text.get("1.0", tk.END).strip()
        sub_date = sub_date_entry.get()
        
        if not all([student_selection, course_selection, title, description, sub_date]):
            raise ValueError("All fields are required!")
        
        # Validate date format
        try:
            datetime.strptime(sub_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Get student ID
        student_id = int(student_selection.split(" - ")[0])
        
        # Get course ID (not by converting course code to int)
        course_code = course_selection.split(" - ")[0]  # Get "CS302" part
        
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            
            # First find the course ID for this course code
            cursor.execute("SELECT course_id FROM courses WHERE course_code = %s", (course_code,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Selected course not found in database")
            course_id = result[0]
            
            # Call stored procedure to create assignment
            cursor.callproc("assign_student_work", 
                          (title, description, faculty_id, student_id, course_id, sub_date))
            conn.commit()
            messagebox.showinfo("Success", "Assignment created successfully!")
            
            # Clear form
            title_entry.delete(0, tk.END)
            desc_text.delete("1.0", tk.END)
            sub_date_entry.delete(0, tk.END)
            
            # Refresh assignments treeview
            for widget in student_cb.master.winfo_children():
                if isinstance(widget, ttk.Treeview):
                    assignments_tree = widget
                    break
            
            for item in assignments_tree.get_children():
                assignments_tree.delete(item)
                
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
        
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error creating assignment: {err}")

# Main application
if __name__ == "__main__":
    # Initialize database
    initialize_database()
    show_login_window()
    
    # Login Screen UI
    root = tk.Tk()
    root.title("Department Management System - Login")
    root.geometry("800x600")
    
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