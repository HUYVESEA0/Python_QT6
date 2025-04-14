# Student Management System

## Overview
This project is a comprehensive Student Management System built with PyQt6. It provides a modern, responsive user interface for managing students, courses, enrollments, and academic reports.

## Features
- Modern Qt6-based user interface
- Complete student record management
- Course catalog and management
- Enrollment system with grade tracking
- Statistical reporting and performance analysis
- User authentication system
- Cross-platform compatibility (Windows, macOS, Linux)
- Responsive design elements
- SQLite database integration

## Dependencies
- Python 3.8+
- PyQt6 >= 6.0.0

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Python_QT6
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application
You can run the application in two ways:

#### Using the batch file (Windows)
```bash
run_app.bat
```

#### Using Python directly
```bash
python main.py
```

### Default Login
- Username: admin
- Password: admin

## Project Structure
- `main.py`: Entry point for the application
- `views/`: UI components for different modules
  - `login_view.py`: Login screen interface
  - `main_window.py`: Main application window
  - `student_view.py`: Student management interface
  - `course_view.py`: Course management interface
  - `enrollment_view.py`: Enrollment management interface
  - `report_view.py`: Reporting and statistics interface
- `controllers/`: Business logic controllers
  - `student_controller.py`: Student data operations
  - `course_controller.py`: Course data operations
  - `user_controller.py`: User authentication and management
  - `report_controller.py`: Reporting and statistics generation
- `models/`: Data models
  - `student.py`: Student entity model
  - `course.py`: Course entity model
  - `user.py`: User entity model
- `DB/`: Database operations
  - `db_manager.py`: SQLite database management
- `utils/`: Utility functions and helper classes
  - `logger.py`: Application logging
  - `helpers.py`: Common helper functions
- `resources/`: Application resources
  - `styles/`: CSS styling files
- `run_app.bat`: Windows batch file to run the application

## Data Storage
The application stores data in a SQLite database located in the `data` directory. Log files are stored in the `logs` directory.

## Features in Detail

### Student Management
- Add, edit, and delete student records
- Search for students by various criteria
- Track enrollment status and academic progress

### Course Management
- Create and manage course offerings
- Set course capacity and instructor information
- Track enrollment statistics

### Enrollment System
- Register students for courses
- Record and manage grades
- View enrollment history

### Reporting
- Overview statistics of students and courses
- Course popularity analytics
- Grade distribution reports
- Individual student performance reports

## License
[Specify your license here]
