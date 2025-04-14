# Python Qt6 GUI Application

## Overview
This project is a GUI application built with PyQt6 that interfaces with a Flask backend. It provides a modern, responsive user interface for interacting with the Flask API.

## Features
- Modern Qt6-based user interface
- Integration with Flask backend services
- Cross-platform compatibility (Windows, macOS, Linux)
- Responsive design elements

## Dependencies
- Python 3.8+
- PyQt6
- Flask
- Requests

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
```bash
python main.py
```

### Configuration
Application settings can be modified in the `config.ini` file.

## Project Structure
- `main.py`: Entry point for the application
- `views/`: Contains UI definition files
- `controllers/`: Contains application logic
- `models/`: Data models for the application
- `utils/`: Utility functions and helper classes

## Development

### Building UI Files
```bash
pyuic6 -o views/ui_main.py views/main.ui
```

### Adding New Features
1. Create UI elements in Qt Designer
2. Generate Python code from .ui files
3. Implement controller logic
4. Update models as necessary

## License
[Specify your license here]
