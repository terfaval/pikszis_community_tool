-- Adds length_minutes to questionnaires for estimated completion time
ALTER TABLE questionnaires
  ADD COLUMN IF NOT EXISTS length_minutes integer;
