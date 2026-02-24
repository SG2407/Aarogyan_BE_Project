# Onboarding session model for medical onboarding
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    current_step = Column(String)
    progress = Column(Float, default=0.0)
    last_question = Column(String)
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_profile = relationship("UserMedicalProfile", uselist=False, primaryjoin="OnboardingSession.user_id==UserMedicalProfile.user_id")
