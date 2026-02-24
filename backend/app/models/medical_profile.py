# Medical profile models for smart onboarding
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserMedicalProfile(Base):
    __tablename__ = "user_medical_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    age = Column(Integer)
    biological_sex = Column(Enum("male", "female", "other", name="biological_sex_enum"))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    pregnancy_status = Column(Boolean)
    smoking_status = Column(String)
    alcohol_consumption = Column(String)
    exercise_frequency = Column(String)
    sleep_duration = Column(Float)
    diet_type = Column(String)
    stress_level = Column(String)
    profile_completion_score = Column(Float, default=0.0)

    chronic_conditions = relationship("ChronicCondition", back_populates="profile")
    medications = relationship("Medication", back_populates="profile")
    allergies = relationship("Allergy", back_populates="profile")
    surgical_history = relationship("SurgicalHistory", back_populates="profile")
    family_history = relationship("FamilyHistory", back_populates="profile")
    lab_values = relationship("LabValue", back_populates="profile")

class ChronicCondition(Base):
    __tablename__ = "chronic_conditions"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    name = Column(String)
    year_diagnosed = Column(Integer, nullable=True)
    controlled_status = Column(Enum("yes", "no", "unknown", name="controlled_status_enum"))
    profile = relationship("UserMedicalProfile", back_populates="chronic_conditions")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    name = Column(String)
    dose = Column(String)
    frequency = Column(String)
    condition = Column(String)
    since = Column(Integer, nullable=True)
    profile = relationship("UserMedicalProfile", back_populates="medications")

class Allergy(Base):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    allergen = Column(String)
    reaction_type = Column(String)
    severity = Column(String)
    profile = relationship("UserMedicalProfile", back_populates="allergies")

class SurgicalHistory(Base):
    __tablename__ = "surgical_history"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    surgery = Column(String)
    year = Column(Integer, nullable=True)
    profile = relationship("UserMedicalProfile", back_populates="surgical_history")

class FamilyHistory(Base):
    __tablename__ = "family_history"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    disease = Column(String)
    relation = Column(String)
    profile = relationship("UserMedicalProfile", back_populates="family_history")

class LabValue(Base):
    __tablename__ = "lab_values"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_medical_profiles.id"))
    name = Column(String)
    value = Column(Float)
    date = Column(Date, nullable=True)
    profile = relationship("UserMedicalProfile", back_populates="lab_values")
