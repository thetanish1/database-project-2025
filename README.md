# <h1> 🏫 Department Management System </h1> 

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/license-MIT-green)

A full-fledged **Department Management System** with role-based access for **HOD**, **Faculty**, and **Students**. This system allows for seamless assignment management, grading, and feedback—all through a user-friendly GUI interface powered by Tkinter.

---

## ✨ Features

### 🔐 Role-Based Access
- **HOD Dashboard**:
  - Assign courses to faculty
  - View workload and performance reports
  - Manage department resources

- **Faculty Dashboard**:
  - Create, assign, and grade student assignments
  - Monitor student submissions
  - Upload course materials

- **Student Dashboard**:
  - View assigned courses and assignments
  - Submit work before deadlines
  - Receive grades and feedback

### ⚙️ Core Functionality
- Authentication and role-based login
- Assignment creation, tracking, and evaluation
- Real-time submission tracking
- MySQL database backend
- Clean and responsive Tkinter GUI

---

## 🛠️ Installation

### ✅ Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- `pip` package manager

### 📦 Setup Instructions

1. **Clone the repository**:
  git clone https://github.com/thetanish1/database-project-2025.git

### Create and activate a virtual environment:
- python -m venv .venv
- .venv\Scripts\activate   # Windows
# OR
- source .venv/bin/activate   # Linux/Mac

### Install dependencies:
- pip install -r requirements.txt

### Configure the database:

# Log into MySQL and create the database:
CREATE DATABASE department_management; 

# Edit config.py with your DB credentials:
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'department_management'
}

# Initialize the database:
python initialize_db.py

# Run the application:
python app.py

### 🔐 Login Credentials
- Added in Database, you can see it from there.

### 🗃️ Database Schema
Key Tables:
users – Stores login credentials and role info
faculty – Faculty member details
students – Student profiles
courses – Course catalog
faculty_assignments – Course-faculty mapping
student_assignments – Assignment submission tracking

### 📁 Project Structure
department-management-system/
├── app.py                # Main application entry point
├── initialize_db.py      # DB setup script
├── config.py             # DB configuration
├── requirements.txt      # Python dependencies
├── docs/                 # Documentation & schema
│   └── db_schema.png
└── README.md             # Project documentation

### 📬 Contact
Maintainer: Tanish Dewase
📧 Email: tanishdewase@duck.com
🔗 Project URL: https://github.com/thetanish1/database-project-2025.git
