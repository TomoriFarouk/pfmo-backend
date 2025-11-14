from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime


class UserRole(enum.Enum):
    ADMIN = "admin"
    DATA_COLLECTOR = "data_collector"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))
    role = Column(Enum(UserRole),
                  default=UserRole.DATA_COLLECTOR, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Additional fields
    notes = Column(Text)

    # Relationships
    submissions = relationship("FormSubmission", back_populates="collector")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"
