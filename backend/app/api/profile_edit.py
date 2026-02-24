# Manual editing endpoints for medical profile
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.medical_profile import UserMedicalProfile, ChronicCondition, Medication, Allergy, SurgicalHistory, FamilyHistory, LabValue

router = APIRouter()

@router.put("/profile/edit", summary="Edit medical profile fields")
def edit_profile(user_id: int, updates: dict, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in updates.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    db.commit()
    return {"profile": profile}

@router.post("/profile/add-condition", summary="Add chronic condition")
def add_condition(user_id: int, condition: dict, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    new_condition = ChronicCondition(profile_id=profile.id, **condition)
    db.add(new_condition)
    db.commit()
    return {"condition": new_condition}

@router.delete("/profile/delete-condition/{condition_id}", summary="Delete chronic condition")
def delete_condition(user_id: int, condition_id: int, db: Session = Depends(get_db)):
    condition = db.query(ChronicCondition).filter_by(id=condition_id).first()
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    db.delete(condition)
    db.commit()
    return {"deleted": True}

@router.post("/profile/add-medication", summary="Add medication")
def add_medication(user_id: int, medication: dict, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    new_med = Medication(profile_id=profile.id, **medication)
    db.add(new_med)
    db.commit()
    return {"medication": new_med}

@router.delete("/profile/delete-medication/{medication_id}", summary="Delete medication")
def delete_medication(user_id: int, medication_id: int, db: Session = Depends(get_db)):
    med = db.query(Medication).filter_by(id=medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return {"deleted": True}

@router.post("/profile/add-allergy", summary="Add allergy")
def add_allergy(user_id: int, allergy: dict, db: Session = Depends(get_db)):
    profile = db.query(UserMedicalProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    new_allergy = Allergy(profile_id=profile.id, **allergy)
    db.add(new_allergy)
    db.commit()
    return {"allergy": new_allergy}

@router.delete("/profile/delete-allergy/{allergy_id}", summary="Delete allergy")
def delete_allergy(user_id: int, allergy_id: int, db: Session = Depends(get_db)):
    allergy = db.query(Allergy).filter_by(id=allergy_id).first()
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    db.delete(allergy)
    db.commit()
    return {"deleted": True}

# Similar endpoints can be added for surgical history, family history, lab values
