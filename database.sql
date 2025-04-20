CREATE DATABASE department_management;
USE department_management;

-- Create Courses Table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100),
    department VARCHAR(50)
);

-- Create Faculty Table
CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
    department VARCHAR(50),
    course_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Create Students Table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
    department VARCHAR(50)
);

-- Create Assignments Table
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    assigned_to INT,
    faculty_id INT,
    submission_date DATE,
    FOREIGN KEY (assigned_to) REFERENCES students(student_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

-- Create Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    role VARCHAR(20)  -- e.g., HOD, Faculty, Student
);


INSERT INTO users (username, password, role) VALUES ('hod1', 'password', 'HOD');
INSERT INTO users (username, password, role) VALUES ('faculty1', 'password', 'Faculty');
INSERT INTO users (username, password, role) VALUES ('student1', 'password', 'Student');


CREATE TABLE faculty_work (
    faculty_work_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT,
    course_id INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

select * from users;

INSERT INTO courses (course_name, department) VALUES
('Data Structures', 'Computer Science'),
('Operating Systems', 'Computer Science'),
('Networks', 'Information Technology'),
('Cybersecurity', 'Information Technology'),
('Artificial Intelligence', 'Computer Science');

INSERT INTO faculty (name, email, phone, department, course_id) VALUES
('Dr. Neha Sharma', 'neha.sharma@example.com', '9876543210', 'Computer Science', 1),
('Prof. Ramesh Patel', 'ramesh.patel@example.com', '9123456780', 'Information Technology', 3),
('Dr. Priya Mehta', 'priya.mehta@example.com', '9988776655', 'Computer Science', 5);

INSERT INTO students (name, email, phone, department) VALUES
('Amit Verma', 'amit.verma@example.com', '9001234567', 'Computer Science'),
('Sneha Kapoor', 'sneha.kapoor@example.com', '9012345678', 'Information Technology'),
('Ravi Jain', 'ravi.jain@example.com', '9023456789', 'Computer Science');

INSERT INTO assignments (title, description, assigned_to, faculty_id, submission_date) VALUES
('Linked List Project', 'Implement singly and doubly linked lists.', 1, 1, '2025-04-25'),
('Networking Basics', 'Submit a report on OSI Model.', 2, 2, '2025-04-27'),
('AI Basics', 'Write a paper on Neural Networks.', 3, 3, '2025-05-01');

-- Already provided by you
-- ('hod1', 'password', 'HOD');
-- ('faculty1', 'password', 'Faculty');
-- ('student1', 'password', 'Student');

-- Optionally link them to real data with actual names
INSERT INTO users (username, password, role) VALUES
('neha_sharma', 'password', 'Faculty'),
('amit_verma', 'password', 'Student'),
('priya_mehta', 'password', 'Faculty'),
('ravi_jain', 'password', 'Student');

INSERT INTO faculty_work (faculty_id, course_id) VALUES
(1, 1),  -- Neha Sharma to Data Structures
(2, 3),  -- Ramesh Patel to Networks
(3, 5);  -- Priya Mehta to AI








