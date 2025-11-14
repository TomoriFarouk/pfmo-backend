from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class FormBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    form_schema: Optional[Dict[str, Any]] = None


class FormCreate(FormBase):
    created_by: Optional[int] = None


class FormUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    form_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None


class FormResponse(FormBase):
    id: int
    is_active: bool
    is_deleted: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
