from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # PFMO Identification Section 1
    pfmo_name = Column(String(200))
    pfmo_phone = Column(String(20))
    geopolitical_zone = Column(String(50))
    state = Column(String(100))
    lga = Column(String(100))
    federal_inec_ward = Column(String(100))
    other_ward = Column(String(100))

    # Health Facility Information Section 2
    facility_name = Column(String(200))
    facility_uid = Column(String(50))
    assessment_type = Column(String(50))
    has_health_workers = Column(String(10))
    facility_condition = Column(String(100))
    ownership_type = Column(String(50))
    ownership_specify = Column(String(200))

    # GPS Coordinates (critical for data collectors)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    accuracy = Column(Float)

    # File uploads
    facility_image_path = Column(String(500))

    # Officer-in-Charge (OIC) Information Section 3
    oic_first_name = Column(String(100))
    oic_last_name = Column(String(100))
    oic_gender = Column(String(10))
    oic_phone = Column(String(20))
    oic_email = Column(String(200))
    oic_signatory = Column(String(10))
    signatory_name = Column(String(200))
    cheque_domicile = Column(String(10))
    cheque_holder = Column(String(200))
    opening_time = Column(String(10))
    closing_time = Column(String(10))

    # Funding Information Section 4 (stored as JSON for flexibility)
    funding_data = Column(JSON)  # BHCPF, IMPACT, other funding details
    impact_funding_data = Column(JSON)  # Detailed IMPACT funding section

    # Infrastructure Section 7
    # Revitalization, components, power, water, etc.
    infrastructure_data = Column(JSON)

    # Human Resources Section 8
    human_resources_data = Column(JSON)  # Staff counts, roles, etc.

    # Services and Utilization Section 9
    services_data = Column(JSON)  # Services rendered, patient counts, etc.

    # Essential Commodities Section 10
    commodities_data = Column(JSON)  # Stock information, commodities

    # Patient Satisfaction Survey Section 11
    satisfaction_survey_data = Column(JSON)  # Patient survey responses

    # Business Plan & Financial Validation Section 5
    financial_validation_data = Column(JSON)

    # Issue Escalation and General Comments Section 12
    issues = Column(Text)
    comments = Column(Text)
    facility_selfie_path = Column(String(500))

    # Metadata
    # pending, synced, failed
    submission_status = Column(String(20), default="pending")
    # pending, syncing, synced, failed
    sync_status = Column(String(20), default="pending")
    is_synced = Column(Boolean, default=False)

    # Raw submission data (for debugging and data integrity)
    raw_submission_data = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    synced_at = Column(DateTime)

    # Relationships
    form = relationship("Form", back_populates="submissions")
    collector = relationship("User", back_populates="submissions")

    def to_dict(self):
        """Convert submission to dictionary with all fields for AI analysis"""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "collector_id": self.collector_id,
            "pfmo_name": self.pfmo_name,
            "pfmo_phone": self.pfmo_phone,
            "geopolitical_zone": self.geopolitical_zone,
            "state": self.state,
            "lga": self.lga,
            "federal_inec_ward": self.federal_inec_ward,
            "other_ward": self.other_ward,
            "facility_name": self.facility_name,
            "facility_uid": self.facility_uid,
            "assessment_type": self.assessment_type,
            "has_health_workers": self.has_health_workers,
            "facility_condition": self.facility_condition,
            "ownership_type": self.ownership_type,
            "ownership_specify": self.ownership_specify,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "accuracy": self.accuracy,
            "oic_first_name": self.oic_first_name,
            "oic_last_name": self.oic_last_name,
            "oic_gender": self.oic_gender,
            "oic_phone": self.oic_phone,
            "oic_email": self.oic_email,
            "funding_data": self.funding_data,
            "impact_funding_data": self.impact_funding_data,
            "infrastructure_data": self.infrastructure_data,
            "human_resources_data": self.human_resources_data,
            "services_data": self.services_data,
            "commodities_data": self.commodities_data,
            "satisfaction_survey_data": self.satisfaction_survey_data,
            "financial_validation_data": self.financial_validation_data,
            "issues": self.issues,
            "comments": self.comments,
            "submission_status": self.submission_status,
            "sync_status": self.sync_status,
            "is_synced": self.is_synced,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<FormSubmission(id={self.id}, facility={self.facility_name}, status={self.sync_status})>"
