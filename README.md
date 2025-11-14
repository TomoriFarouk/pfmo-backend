# PFMO Data Collection Backend

Python FastAPI backend for the PFMO (Primary Healthcare Facility Management Organization) Data Collection System.

## Features

- 🔐 User authentication with JWT tokens
- 📝 Form management (create, read, update, delete)
- 📊 Form submission handling with offline support
- 📍 GPS coordinate tracking
- 📁 File upload support (images, documents)
- 📈 Dashboard statistics and analytics
- 🔄 Data sync between mobile app and backend
- 👥 User and data collector management

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create uploads directory:
```bash
mkdir uploads
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Update the `SECRET_KEY` in `.env` file for production use.

## Running the Server

```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Credentials

After first run, the system creates a default admin user:
- **Username:** admin
- **Password:** admin123

**⚠️ Change these credentials in production!**

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Submissions
- `POST /api/v1/submissions/submit` - Submit new form
- `GET /api/v1/submissions/submissions` - Get all submissions
- `GET /api/v1/submissions/submissions/{id}` - Get specific submission
- `PUT /api/v1/submissions/submissions/{id}` - Update submission
- `DELETE /api/v1/submissions/submissions/{id}` - Delete submission (admin)
- `POST /api/v1/submissions/upload` - Upload files
- `GET /api/v1/submissions/stats` - Get submission statistics

### Forms
- `POST /api/v1/forms/create` - Create new form (admin)
- `GET /api/v1/forms/forms` - Get all forms
- `GET /api/v1/forms/forms/{id}` - Get specific form
- `PUT /api/v1/forms/forms/{id}` - Update form (admin)
- `DELETE /api/v1/forms/forms/{id}` - Delete form (admin)

### Dashboard
- `GET /api/v1/dashboard/overview` - Get dashboard overview (admin)
- `GET /api/v1/dashboard/geographic-data` - Get geographic data (admin)
- `GET /api/v1/dashboard/collectors` - Get collector stats (admin)

## Database

The application uses SQLite by default. Database file: `pfmo_data.db`

### Models

- **User**: Authentication and user management
- **Form**: Form templates and definitions
- **FormSubmission**: Submitted form data with all PFMO fields

## Development

To run in development mode with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
pytest
```

## Deployment

For production deployment, consider:
- Using PostgreSQL instead of SQLite
- Setting up proper SSL/TLS
- Using environment variables for secrets
- Setting up proper CORS origins
- Using a production WSGI server like Gunicorn

