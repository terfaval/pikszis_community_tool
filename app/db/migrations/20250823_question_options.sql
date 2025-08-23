-- 20250823_question_options.sql
-- Stores answer options for choice-based questions
CREATE TABLE IF NOT EXISTS question_options (
    id bigserial PRIMARY KEY,
    question_id bigint NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    ord int NOT NULL,
    label text NOT NULL,
    value text,
    UNIQUE (question_id, ord)
);