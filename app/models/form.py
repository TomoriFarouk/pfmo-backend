from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(50))

    # Form definition (JSON structure for dynamic forms)
    form_schema = Column(JSON)

    # Metadata
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    submissions = relationship("FormSubmission", back_populates="form")

    def __repr__(self):
        return f"<Form(id={self.id}, name={self.name}, version={self.version})>"
