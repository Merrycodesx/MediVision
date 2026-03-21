# How to Run the MediVision Frontend

This guide provides step-by-step instructions to set up and run the MediVision frontend web application.

## Prerequisites

- Python 3.8 or higher installed on your system
- Git (for cloning the repository if not already done)
- Access to the MediVision project repository

## Step 1: Set Up the Project Environment

1. **Clone the Repository** (if not already cloned):
   ```
   git clone <repository-url>
   cd MediVision
   ```

2. **Create a Virtual Environment**:
   - Run: `python -m venv medV-env`
   - This creates an isolated Python environment for the project.

3. **Activate the Virtual Environment**:
   - On Windows: `medV-env\Scripts\activate`
   - On macOS/Linux: `source medV-env/bin/activate`
   - Your command prompt should now show `(medV-env)` at the beginning.

4. **Install Dependencies**:
   - Run: `pip install -r requirements.txt`
   - This installs all required Python packages for both backend and AI components.

## Step 2: Set Up and Run the Backend

The frontend requires the Django backend API to function properly.

1. **Navigate to Backend Directory**:
   - Run: `cd medV_backend`

2. **Create Environment Configuration**:
   - Create a `.env` file in the `medV_backend` directory with the following content:
     ```
     SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
     DEBUG=True
     ENGINE=django.db.backends.sqlite3
     DB_NAME=db.sqlite3
     DB_USER=
     PASSWORD=
     HOST=
     PORT=
     ```

3. **Run Database Migrations**:
   - Run: `python manage.py migrate`
   - This sets up the SQLite database with the required tables.

4. **Start the Backend Server**:
   - Run: `python manage.py runserver`
   - The backend API will start on `http://127.0.0.1:8000/`
   - Keep this terminal running (the server runs in the background).

## Step 3: Run the Frontend

1. **Open a New Terminal Window**:
   - Keep the backend server running in the previous terminal.
   - Open a new PowerShell/Command Prompt window.

2. **Navigate to Frontend Directory**:
   - Run: `cd MediVision\frontend`

3. **Start the Frontend Server**:
   - Run: `python -m http.server 3000`
   - This starts a simple HTTP server on port 3000.

4. **Access the Application**:
   - Open your web browser.
   - Navigate to: `http://localhost:3000/`
   - The MediVision frontend should now load and connect to the backend API.

## Troubleshooting

- **Port Conflicts**: If port 3000 is in use, change to another port: `python -m http.server 8080`
- **Backend Connection Issues**: Ensure the backend is running on port 8000 and the frontend can reach it.
- **Python Path Issues**: Make sure you're using the virtual environment's Python.
- **Permission Errors**: Run terminals as administrator if needed.

## Stopping the Application

- Press `Ctrl+C` in each terminal to stop the servers.
- Deactivate the virtual environment: `deactivate`

## Development Notes

- The frontend is a single-page application built with vanilla JavaScript, HTML, and CSS.
- It communicates with the Django REST API for data operations.
- For production deployment, consider using a proper web server like Nginx and a production database.