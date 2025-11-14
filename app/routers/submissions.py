from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import os
import shutil

from app.database import get_db
from app.models.submission import FormSubmission
from app.models.user import User, UserRole
from app.schemas.submission import SubmissionCreate, SubmissionResponse, SubmissionUpdate
from app.routers.auth import get_current_user, get_current_active_admin
from app.core.config import settings

router = APIRouter()


@router.post("/submit", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_form(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a new form"""
    submission_data = submission.dict(exclude_unset=True)

    # Add collector ID
    submission_data["collector_id"] = current_user.id
    submission_data["raw_submission_data"] = submission_data.copy()

    db_submission = FormSubmission(
        **submission_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission


@router.get("/submissions", response_model=List[SubmissionResponse])
def get_submissions(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    sync_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all submissions with optional filters"""
    query = db.query(FormSubmission)

    # Filter by role
    if current_user.role == UserRole.DATA_COLLECTOR:
        query = query.filter(FormSubmission.collector_id == current_user.id)

    # Apply filters
    if state:
        query = query.filter(FormSubmission.state == state)
    if lga:
        query = query.filter(FormSubmission.lga == lga)
    if sync_status:
        query = query.filter(FormSubmission.sync_status == sync_status)

    submissions = query.order_by(
        desc(FormSubmission.created_at)).offset(skip).limit(limit).all()
    return submissions


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific submission by ID"""
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permissions
    if current_user.role == UserRole.DATA_COLLECTOR and submission.collector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return submission


@router.put("/submissions/{submission_id}", response_model=SubmissionResponse)
def update_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a submission"""
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permissions
    if current_user.role == UserRole.DATA_COLLECTOR and submission.collector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update fields
    update_data = submission_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(submission, field, value)

    submission.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    return submission


@router.delete("/submissions/{submission_id}")
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_admin)  # Only admins can delete
):
    """Delete a submission (admin only)"""
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    db.delete(submission)
    db.commit()

    return {"message": "Submission deleted successfully"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file (e.g., facility image)"""
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    unique_filename = f"{datetime.utcnow().timestamp()}_{current_user.id}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "file_path": file_path,
        "filename": unique_filename,
        "original_filename": file.filename
    }


@router.get("/stats")
def get_submission_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get submission statistics"""
    query = db.query(FormSubmission)

    # Filter by role
    if current_user.role == UserRole.DATA_COLLECTOR:
        query = query.filter(FormSubmission.collector_id == current_user.id)

    total = query.count()
    synced = query.filter(FormSubmission.is_synced == True).count()
    pending = query.filter(FormSubmission.sync_status == "pending").count()

    return {
        "total_submissions": total,
        "synced_submissions": synced,
        "pending_submissions": pending,
        "sync_percentage": round((synced / total * 100) if total > 0 else 0, 2)
    }
