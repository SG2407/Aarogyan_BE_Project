# Onboarding API endpoints for medical profile
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.medical_profile import UserMedicalProfile
from app.models.onboarding_session import OnboardingSession
from app.core.profile_scoring import calculate_profile_completion
from typing import Optional
import re

router = APIRouter()

@router.get("/onboarding/profile", summary="Get user medical profile and completion score")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not profile:
        # Auto-create empty medical profile for user
        profile = UserMedicalProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    score = calculate_profile_completion(profile)
    # Optionally, trigger onboarding session if not present
    session = db.query(OnboardingSession).filter_by(user_id=user_id).first()
    next_question = None
    if session and session.is_active:
        next_question = session.current_step
    return {"profile": profile, "completion_score": score, "next_question": next_question}

@router.post("/onboarding/start", summary="Start onboarding session")
def start_onboarding(user_id: int, db: Session = Depends(get_db)):
    session = db.query(OnboardingSession).filter_by(user_id=user_id).first()
    if session and session.is_active:
        return {"session": session}
    session = OnboardingSession(user_id=user_id, is_active=True)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session": session}

@router.post("/onboarding/answer", summary="Submit onboarding answer and update profile")
def submit_answer(user_id: int, answer: dict, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    session = db.query(OnboardingSession).filter_by(user_id=user_id).first()
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="No active onboarding session")

    # --- Structured Data Extraction ---
    # This is a simple rule-based extraction. Replace with LLM if needed.
    def extract_field(field, answer):
        if field == 'age':
            m = re.search(r'(\d{1,3})', str(answer.get('age', answer.get('response', ''))))
            return int(m.group(1)) if m else None
        if field == 'biological_sex':
            val = str(answer.get('biological_sex', answer.get('response', '')).lower())
            if 'male' in val:
                return 'male'
            if 'female' in val:
                return 'female'
            if 'other' in val:
                return 'other'
            return None
        # Add more extraction rules as needed
        return answer.get(field)

    # --- Adaptive Question Logic ---
    def get_next_question(profile):
        # Prioritize critical, then important, then enhancement
        for field in CRITICAL_FIELDS:
            if not getattr(profile, field) and not (field == 'chronic_conditions' and profile.chronic_conditions) and not (field == 'medications' and profile.medications) and not (field == 'allergies' and profile.allergies):
                return field
        for field in IMPORTANT_FIELDS:
            if not getattr(profile, field):
                return field
        for field in ENHANCEMENT_FIELDS:
            if not getattr(profile, field):
                return field
        return None

    # --- Update Profile ---
    current_field = session.current_step or get_next_question(profile)
    if current_field:
        value = extract_field(current_field, answer)
        if value is not None:
            setattr(profile, current_field, value)
        session.last_question = current_field
        db.commit()

    # --- Recalculate Score ---
    score = calculate_profile_completion(profile)
    session.progress = score
    db.commit()
    if score >= 70:
        session.is_active = False
        db.commit()

    # --- Decide Next Step ---
    next_field = get_next_question(profile)
    session.current_step = next_field
    db.commit()
    return {
        "completion_score": score,
        "session": session,
        "next_question": next_field
    }

@router.post("/onboarding/skip", summary="Skip current onboarding question")
def skip_question(user_id: int, db: Session = Depends(get_db)):
    session = db.query(OnboardingSession).filter_by(user_id=user_id).first()
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="No active onboarding session")
    # Move to next missing field
    def get_next_question(profile):
        for field in CRITICAL_FIELDS:
            if not getattr(profile, field) and not (field == 'chronic_conditions' and profile.chronic_conditions) and not (field == 'medications' and profile.medications) and not (field == 'allergies' and profile.allergies):
                return field
        for field in IMPORTANT_FIELDS:
            if not getattr(profile, field):
                return field
        for field in ENHANCEMENT_FIELDS:
            if not getattr(profile, field):
                return field
        return None
    next_field = get_next_question(profile)
    session.current_step = next_field
    db.commit()
    return {"session": session, "next_question": next_field}

@router.post("/onboarding/end", summary="End onboarding session manually")
def end_onboarding(user_id: int, db: Session = Depends(get_db)):
    session = db.query(OnboardingSession).filter_by(user_id=user_id).first()
    if session:
        session.is_active = False
        db.commit()
    return {"session": session}
