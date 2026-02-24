# Onboarding API endpoints for medical profile
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
class OnboardingAnswerRequest(BaseModel):
    user_id: str
    answer: dict

class OnboardingSkipRequest(BaseModel):
    user_id: str
from app.core.database import get_supabase
## ORM model imports removed; only Supabase client is used
from app.core.profile_scoring import calculate_profile_completion, CRITICAL_FIELDS, IMPORTANT_FIELDS, ENHANCEMENT_FIELDS
from typing import Optional
import re

router = APIRouter()

@router.get("/onboarding/profile", summary="Get user medical profile and completion score")
def get_profile(user_id: str, supabase=Depends(get_supabase)):
    # Fetch medical profile from Supabase using UUID user_id
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not profile:
        # Auto-create empty medical profile for user (UUID)
        insert_resp = supabase.table("user_medical_profiles").insert({"user_id": user_id}).execute()
        profile = insert_resp.data[0]
    score = calculate_profile_completion(profile)
    # Ensure onboarding session exists and is active
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    if not session or not session.get("is_active", False):
        # Create a new onboarding session if missing or inactive
        insert_resp = supabase.table("onboarding_sessions").insert({"user_id": user_id, "is_active": True}).execute()
        session = insert_resp.data[0]
    # Determine next question
    next_question = session.get("current_step")
    if not next_question:
        # If current_step is not set, pick the first unanswered field
        for field in CRITICAL_FIELDS + IMPORTANT_FIELDS + ENHANCEMENT_FIELDS:
            if not profile.get(field):
                next_question = field
                supabase.table("onboarding_sessions").update({"current_step": next_question}).eq("user_id", user_id).execute()
                break
    return {"profile": profile, "completion_score": score, "next_question": next_question}

@router.post("/onboarding/start", summary="Start onboarding session")
def start_onboarding(user_id: str, supabase=Depends(get_supabase)):
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    if session and session["is_active"]:
        return {"session": session}
    insert_resp = supabase.table("onboarding_sessions").insert({"user_id": user_id, "is_active": True}).execute()
    session = insert_resp.data[0]
    return {"session": session}

@router.post("/onboarding/answer", summary="Submit onboarding answer and update profile")
def submit_answer(request: OnboardingAnswerRequest, supabase=Depends(get_supabase)):
    user_id = request.user_id
    answer = request.answer
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    if not session or not session["is_active"]:
        raise HTTPException(status_code=400, detail="No active onboarding session")

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
        return answer.get(field)

    def get_next_question(profile):
        for field in CRITICAL_FIELDS:
            if not profile.get(field):
                return field
        for field in IMPORTANT_FIELDS:
            if not profile.get(field):
                return field
        for field in ENHANCEMENT_FIELDS:
            if not profile.get(field):
                return field
        return None

    current_field = session.get("current_step") or get_next_question(profile)
    if current_field:
        value = extract_field(current_field, answer)
        if value is not None:
            supabase.table("user_medical_profiles").update({current_field: value}).eq("user_id", user_id).execute()
        supabase.table("onboarding_sessions").update({"last_question": current_field}).eq("user_id", user_id).execute()

    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    score = calculate_profile_completion(profile)
    supabase.table("onboarding_sessions").update({"progress": score}).eq("user_id", user_id).execute()
    if score >= 70:
        supabase.table("onboarding_sessions").update({"is_active": False}).eq("user_id", user_id).execute()

    next_field = get_next_question(profile)
    supabase.table("onboarding_sessions").update({"current_step": next_field}).eq("user_id", user_id).execute()
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    return {
        "profile": profile,
        "completion_score": score,
        "session": session,
        "next_question": next_field
    }

@router.post("/onboarding/skip", summary="Skip current onboarding question")
def skip_question(request: OnboardingSkipRequest, supabase=Depends(get_supabase)):
    user_id = request.user_id
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not session or not session["is_active"]:
        raise HTTPException(status_code=400, detail="No active onboarding session")
    def get_next_question(profile):
        for field in CRITICAL_FIELDS:
            if not profile.get(field):
                return field
        for field in IMPORTANT_FIELDS:
            if not profile.get(field):
                return field
        for field in ENHANCEMENT_FIELDS:
            if not profile.get(field):
                return field
        return None
    next_field = get_next_question(profile)
    supabase.table("onboarding_sessions").update({"current_step": next_field}).eq("user_id", user_id).execute()
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    # Also return updated profile and completion_score for frontend state sync
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    score = calculate_profile_completion(profile)
    return {
        "profile": profile,
        "completion_score": score,
        "session": session,
        "next_question": next_field
    }

@router.post("/onboarding/end", summary="End onboarding session manually")
def end_onboarding(user_id: str, supabase=Depends(get_supabase)):
    session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
    session = session_resp.data[0] if session_resp.data else None
    if session:
        supabase.table("onboarding_sessions").update({"is_active": False}).eq("user_id", user_id).execute()
        session_resp = supabase.table("onboarding_sessions").select("*").eq("user_id", user_id).execute()
        session = session_resp.data[0] if session_resp.data else None
    return {"session": session}
