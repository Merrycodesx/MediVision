# MediVision Project

MediVision is a medical AI project consisting of three main components:
- **Backend (medV_backend)**: Django REST API for handling user authentication, patient data, and CXR image management.
- **AI Module (medi_ai)**: Machine learning models for image processing and TB label extraction.
- **Desktop App (medV-Desktop)**: PyQt5-based desktop application for user interaction.

## Prerequisites

- Python 3.8 or higher
- Git
- (Optional) PostgreSQL for production database (local development uses SQLite)

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MediVision
```

### 2. Set Up Virtual Environment

```bash
python -m venv medV-env
# On Windows
medV-env\Scripts\activate
# On macOS/Linux
source medV-env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Backend Setup

Navigate to the backend directory:

```bash
cd medV_backend
```

Create a `.env` file for environment variables (copy from `.env.example` if available):

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL for production
```

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### 5. AI Module Setup

The AI module is integrated into the backend. Ensure the `medi_ai` directory is accessible.

For standalone testing, you can run scripts from `medi_ai/`:

```bash
cd medi_ai
python -c "from data.loader import load_data; print('AI module loaded')"
```


## API Endpoints

The backend provides the following main APIs (based on recent commits):

- **Authentication**: JWT-based login/logout
- **User Management**: CRUD operations for users
- **Patient Management**: CRUD operations for patients
- **CXR Image Management**: Upload and process chest X-ray images

Refer to the backend code in `medV_backend/api/` for detailed endpoints.

## Development

- Use the virtual environment for all Python operations.
- For database changes, create and run migrations: `python manage.py makemigrations && python manage.py migrate`
- Test the AI models using the data loader in `medi_ai/data/loader.py`

## Deployment

For production deployment, consider using Docker (see Dockerfile) and a production database like PostgreSQL.

## Contributing

See the documentation section below for how to document changes.