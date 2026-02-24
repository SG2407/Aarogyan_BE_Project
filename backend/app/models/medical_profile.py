# Medical profile models for smart onboarding
# This file is now a reference for Supabase table fields.
# All ORM/SQLAlchemy code removed.

# user_medical_profiles table fields:
# id, user_id, age, biological_sex, height_cm, weight_kg, pregnancy_status, smoking_status, alcohol_consumption,
# exercise_frequency, sleep_duration, diet_type, stress_level, profile_completion_score

# chronic_conditions table fields:
# id, profile_id, name, year_diagnosed, controlled_status

# medications table fields:
# id, profile_id, name, dose, frequency, condition, since

# allergies table fields:
# id, profile_id, allergen, reaction_type, severity

# surgical_history table fields:
# id, profile_id, surgery, year

# family_history table fields:
# id, profile_id, disease, relation

# lab_values table fields:
# id, profile_id, name, value, date
