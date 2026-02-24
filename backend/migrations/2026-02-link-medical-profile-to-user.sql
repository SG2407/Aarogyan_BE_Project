-- Migration: Link medical profile to authentication user (UUID)
-- Change user_id in user_medical_profiles and onboarding_sessions to UUID

-- Step 1: Add new UUID user_id column to user_medical_profiles
ALTER TABLE user_medical_profiles ADD COLUMN user_id_uuid UUID;

-- Step 2: Copy values from old user_id (if possible, if you have a mapping)
-- (Skip if not possible, or set manually)

-- Step 3: Drop old user_id column and rename new column
ALTER TABLE user_medical_profiles DROP COLUMN user_id;
ALTER TABLE user_medical_profiles RENAME COLUMN user_id_uuid TO user_id;

-- Step 4: Add foreign key constraint
ALTER TABLE user_medical_profiles ADD CONSTRAINT fk_user_medical_profiles_user_id FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Step 5: Update onboarding_sessions user_id to UUID
ALTER TABLE onboarding_sessions ADD COLUMN user_id_uuid UUID;
ALTER TABLE onboarding_sessions DROP COLUMN user_id;
ALTER TABLE onboarding_sessions RENAME COLUMN user_id_uuid TO user_id;
ALTER TABLE onboarding_sessions ADD CONSTRAINT fk_onboarding_sessions_user_id FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- All other tables remain unchanged (profile_id links to user_medical_profiles.id)

-- Note: If you have existing data, you may need to manually map old user_id INTEGER to new UUID user_id.
-- If you want to preserve old data, please provide a mapping or let me know for a custom migration.
