from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SubmissionBase(BaseModel):
    form_id: Optional[int] = None
    collector_id: Optional[int] = None

    # PFMO Identification
    pfmo_name: Optional[str] = None
    pfmo_phone: Optional[str] = None
    geopolitical_zone: Optional[str] = None
    state: Optional[str] = None
    lga: Optional[str] = None
    federal_inec_ward: Optional[str] = None
    other_ward: Optional[str] = None

    # Health Facility Info
    facility_name: Optional[str] = None
    facility_uid: Optional[str] = None
    assessment_type: Optional[str] = None
    has_health_workers: Optional[str] = None
    facility_condition: Optional[str] = None
    ownership_type: Optional[str] = None
    ownership_specify: Optional[str] = None

    # GPS Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    accuracy: Optional[float] = None

    # File paths
    facility_image_path: Optional[str] = None

    # OIC Information
    oic_first_name: Optional[str] = None
    oic_last_name: Optional[str] = None
    oic_gender: Optional[str] = None
    oic_phone: Optional[str] = None
    oic_email: Optional[str] = None
    oic_signatory: Optional[str] = None
    signatory_name: Optional[str] = None
    cheque_domicile: Optional[str] = None
    cheque_holder: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None

    # JSON data fields
    funding_data: Optional[Dict[str, Any]] = None
    impact_funding_data: Optional[Dict[str, Any]] = None
    infrastructure_data: Optional[Dict[str, Any]] = None
    human_resources_data: Optional[Dict[str, Any]] = None
    services_data: Optional[Dict[str, Any]] = None
    commodities_data: Optional[Dict[str, Any]] = None
    satisfaction_survey_data: Optional[Dict[str, Any]] = None
    financial_validation_data: Optional[Dict[str, Any]] = None

    # Issue escalation
    issues: Optional[str] = None
    comments: Optional[str] = None
    facility_selfie_path: Optional[str] = None

    # Metadata
    submission_status: Optional[str] = "pending"
    sync_status: Optional[str] = "pending"
    raw_submission_data: Optional[Dict[str, Any]] = None


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    submission_status: Optional[str] = None
    sync_status: Optional[str] = None
    is_synced: Optional[bool] = None


class SubmissionResponse(SubmissionBase):
    id: int
    collector_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    synced_at: Optional[datetime] = None
    is_synced: bool

    class Config:
        from_attributes = True
