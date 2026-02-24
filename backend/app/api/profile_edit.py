# Manual editing endpoints for medical profile
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_supabase
from app.core.profile_scoring import CRITICAL_FIELDS, IMPORTANT_FIELDS, ENHANCEMENT_FIELDS

router = APIRouter()

@router.put("/profile/edit", summary="Edit medical profile fields")
def edit_profile(user_id: int, updates: dict, supabase=Depends(get_supabase)):
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    update_fields = {k: v for k, v in updates.items() if k in CRITICAL_FIELDS + IMPORTANT_FIELDS + ENHANCEMENT_FIELDS}
    supabase.table("user_medical_profiles").update(update_fields).eq("user_id", user_id).execute()
    updated_profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    updated_profile = updated_profile_resp.data[0] if updated_profile_resp.data else None
    return {"profile": updated_profile}

@router.post("/profile/add-condition", summary="Add chronic condition")
def add_condition(user_id: int, condition: dict, supabase=Depends(get_supabase)):
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    condition_data = {"profile_id": profile["id"], **condition}
    insert_resp = supabase.table("chronic_conditions").insert(condition_data).execute()
    return {"condition": insert_resp.data[0] if insert_resp.data else None}

@router.delete("/profile/delete-condition/{condition_id}", summary="Delete chronic condition")
def delete_condition(user_id: int, condition_id: int, supabase=Depends(get_supabase)):
    delete_resp = supabase.table("chronic_conditions").delete().eq("id", condition_id).execute()
    return {"deleted": True}

@router.post("/profile/add-medication", summary="Add medication")
def add_medication(user_id: int, medication: dict, supabase=Depends(get_supabase)):
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    med_data = {"profile_id": profile["id"], **medication}
    insert_resp = supabase.table("medications").insert(med_data).execute()
    return {"medication": insert_resp.data[0] if insert_resp.data else None}

@router.delete("/profile/delete-medication/{medication_id}", summary="Delete medication")
def delete_medication(user_id: int, medication_id: int, supabase=Depends(get_supabase)):
    delete_resp = supabase.table("medications").delete().eq("id", medication_id).execute()
    return {"deleted": True}

@router.post("/profile/add-allergy", summary="Add allergy")
def add_allergy(user_id: int, allergy: dict, supabase=Depends(get_supabase)):
    profile_resp = supabase.table("user_medical_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else None
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    allergy_data = {"profile_id": profile["id"], **allergy}
    insert_resp = supabase.table("allergies").insert(allergy_data).execute()
    return {"allergy": insert_resp.data[0] if insert_resp.data else None}

@router.delete("/profile/delete-allergy/{allergy_id}", summary="Delete allergy")
def delete_allergy(user_id: int, allergy_id: int, supabase=Depends(get_supabase)):
    delete_resp = supabase.table("allergies").delete().eq("id", allergy_id).execute()
    return {"deleted": True}

# Similar endpoints can be added for surgical history, family history, lab values
