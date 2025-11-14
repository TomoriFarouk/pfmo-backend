from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, get_db
from app.routers import auth, submissions, forms, dashboard, ai_insights
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.form import Form
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PFMO Data Collection API",
    description="API for PFMO Data Collection System",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(submissions.router,
                   prefix="/api/v1/submissions", tags=["submissions"])
app.include_router(forms.router, prefix="/api/v1/forms", tags=["forms"])
app.include_router(
    dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(
    ai_insights.router, prefix="/api/v1/ai", tags=["ai-insights"])


@app.get("/")
def root():
    return {
        "message": "PFMO Data Collection API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database with default admin user"""
    db = next(get_db())

    # Check if admin user exists
    admin_user = db.query(User).filter(
        User.username == settings.ADMIN_USERNAME).first()

    if not admin_user:
        # Create default admin user
        admin_user = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_FULL_NAME,
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        print(f"✓ Default admin user created: {settings.ADMIN_USERNAME}")

    # Create default form if none exists
    existing_form = db.query(Form).filter(
        Form.name == "PFMO Data Collection Form"
    ).first()
    if not existing_form:
        default_form_schema = {
            "fields": [
                {"name": "pfmo_name", "label": "PFMO Name",
                    "type": "text", "required": True},
                {"name": "pfmo_phone", "label": "PFMO Phone",
                    "type": "phone", "required": True},
                {"name": "geopolitical_zone", "label": "Geopolitical Zone", "type": "select", "required": True,
                 "options": ["North Central", "North East", "North West", "South East", "South South", "South West"]},
                {"name": "state", "label": "State",
                    "type": "text", "required": True},
                {"name": "lga", "label": "LGA", "type": "text", "required": True},
                {"name": "federal_inec_ward",
                    "label": "Federal INEC Ward", "type": "text"},
                {"name": "other_ward", "label": "Other Ward", "type": "text"},
                {"name": "facility_name", "label": "Facility Name",
                    "type": "text", "required": True},
                {"name": "facility_uid", "label": "Facility UID", "type": "text"},
                {"name": "assessment_type", "label": "Assessment Type", "type": "select",
                 "options": ["Initial", "Follow-up", "Reassessment"]},
                {"name": "has_health_workers", "label": "Has Health Workers", "type": "select",
                 "options": ["Yes", "No"]},
                {"name": "facility_condition", "label": "Facility Condition", "type": "select",
                 "options": ["Good", "Fair", "Poor", "Critical"]},
                {"name": "ownership_type", "label": "Ownership Type", "type": "select",
                 "options": ["Public", "Private", "NGO", "Other"]},
            ]
        }

        default_form = Form(
            name="PFMO Data Collection Form",
            description="Primary Healthcare Facility Data Collection Form - Complete assessment form with 12 sections",
            version="2.0",
            form_schema=default_form_schema,
            is_active=True,
            is_deleted=False,
            created_by=admin_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(default_form)
        db.commit()
        print("✓ Default PFMO form created with schema")

    db.close()
    print("✓ Database initialized successfully")

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
