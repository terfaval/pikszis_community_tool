-- Idempotens sémafrissítés az admin kérdőív builderhez

-- questionnaires: description, in_random_pool
ALTER TABLE questionnaires
  ADD COLUMN IF NOT EXISTS description text;

ALTER TABLE questionnaires
  ADD COLUMN IF NOT EXISTS in_random_pool boolean;

-- Állítsunk biztonságos defaultot és NOT NULL-t (idempotens módon)
UPDATE questionnaires SET in_random_pool = COALESCE(in_random_pool, true);
ALTER TABLE questionnaires ALTER COLUMN in_random_pool SET DEFAULT true;
ALTER TABLE questionnaires ALTER COLUMN in_random_pool SET NOT NULL;

-- questions: required, in_random_pool
ALTER TABLE questions
  ADD COLUMN IF NOT EXISTS required boolean;

ALTER TABLE questions
  ADD COLUMN IF NOT EXISTS in_random_pool boolean;

UPDATE questions
SET required = COALESCE(required, false),
    in_random_pool = COALESCE(in_random_pool, true);

ALTER TABLE questions ALTER COLUMN required SET DEFAULT false;
ALTER TABLE questions ALTER COLUMN required SET NOT NULL;

ALTER TABLE questions ALTER COLUMN in_random_pool SET DEFAULT true;
ALTER TABLE questions ALTER COLUMN in_random_pool SET NOT NULL;
