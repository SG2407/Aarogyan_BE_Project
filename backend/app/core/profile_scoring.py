# Profile completion scoring logic for medical onboarding


CRITICAL_FIELDS = [
    'age', 'biological_sex', 'chronic_conditions', 'medications', 'allergies'
]
IMPORTANT_FIELDS = [
    'height_cm', 'weight_kg', 'pregnancy_status', 'surgical_history', 'family_history', 'smoking_status', 'alcohol_consumption'
]
ENHANCEMENT_FIELDS = [
    'lab_values', 'exercise_frequency', 'sleep_duration', 'diet_type', 'stress_level'
]

WEIGHTS = {
    'critical': 0.5,
    'important': 0.3,
    'enhancement': 0.2
}


def calculate_profile_completion(profile: dict) -> float:
    # Critical fields
    critical_total = len(CRITICAL_FIELDS)
    critical_filled = sum([
        1 if getattr(profile, field) or (field == 'chronic_conditions' and profile.chronic_conditions) or (field == 'medications' and profile.medications) or (field == 'allergies' and profile.allergies) else 0
        for field in CRITICAL_FIELDS
    ])
    critical_score = (critical_filled / critical_total) * WEIGHTS['critical'] * 100

    # Important fields
    important_total = len(IMPORTANT_FIELDS)
    important_filled = sum([
        1 if getattr(profile, field) or (field == 'surgical_history' and profile.surgical_history) or (field == 'family_history' and profile.family_history) else 0
        for field in IMPORTANT_FIELDS
    ])
    important_score = (important_filled / important_total) * WEIGHTS['important'] * 100

    # Enhancement fields
    enhancement_total = len(ENHANCEMENT_FIELDS)
    enhancement_filled = sum([
        1 if getattr(profile, field) or (field == 'lab_values' and profile.lab_values) else 0
        for field in ENHANCEMENT_FIELDS
    ])
    enhancement_score = (enhancement_filled / enhancement_total) * WEIGHTS['enhancement'] * 100

    total_score = critical_score + important_score + enhancement_score
    return round(total_score, 2)
