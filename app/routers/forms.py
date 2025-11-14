from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.form import Form
from app.schemas.form import FormCreate, FormResponse, FormUpdate
from app.routers.auth import get_current_user, get_current_active_admin

router = APIRouter()


@router.post("/create", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
def create_form(
    form: FormCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Create a new form (admin only)"""
    db_form = Form(
        name=form.name,
        description=form.description,
        version=form.version,
        form_schema=form.form_schema,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(db_form)
    db.commit()
    db.refresh(db_form)

    return db_form


@router.get("/forms", response_model=List[FormResponse])
def get_forms(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all forms"""
    query = db.query(Form)

    if active_only:
        query = query.filter(Form.is_active == True, Form.is_deleted == False)

    forms = query.all()
    return forms


@router.get("/forms/{form_id}", response_model=FormResponse)
def get_form(
    form_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific form by ID"""
    form = db.query(Form).filter(Form.id == form_id).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    return form


@router.put("/forms/{form_id}", response_model=FormResponse)
def update_form(
    form_id: int,
    form_update: FormUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Update a form (admin only)"""
    form = db.query(Form).filter(Form.id == form_id).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    update_data = form_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(form, field, value)

    form.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(form)

    return form


@router.delete("/forms/{form_id}")
def delete_form(
    form_id: int,
    permanent: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Delete a form (admin only)

    Args:
        permanent: If True, permanently delete the form. If False, soft delete (mark as inactive).
    """
    form = db.query(Form).filter(Form.id == form_id).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if permanent:
        # Permanent delete - check if form has submissions
        from app.models.submission import FormSubmission
        submission_count = db.query(FormSubmission).filter(
            FormSubmission.form_id == form_id).count()

        if submission_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot permanently delete form with {submission_count} submission(s). Please delete submissions first or use soft delete."
            )

        db.delete(form)
        db.commit()
        return {"message": "Form permanently deleted"}
    else:
        # Soft delete
        form.is_deleted = True
        form.is_active = False
        form.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Form deactivated (soft delete)"}
