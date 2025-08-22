create type if not exists q_type as enum (
  'likert_1_5','likert_1_4','single_choice','multiple_choice','open_text','other'
);
create type if not exists q_status as enum ('draft','submitted');
create type if not exists q_mode as enum ('random','targeted','idea','community');

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text not null,
  display_name text not null,
  created_at timestamptz default now()
);

create table if not exists questionnaires (
  id text primary key,
  title text,
  version text default '1.0.0',
  is_minor_allowed bool,
  requires_guardian_permission_level text default 'general',
  mode q_mode default 'random',
  in_random_pool bool default true,
  eligible_if text,
  is_active bool default true,
  created_at timestamptz default now()
);

create table if not exists questions (
  id text primary key,
  questionnaire_id text references questionnaires(id),
  title text,
  instructions text,
  qtype q_type,
  likert_variant text,
  required bool,
  random_order bool,
  ord int,
  branch_rules jsonb,
  random_multi bool,
  in_random_pool bool,
  following text
);

create table if not exists submissions (
  id uuid primary key default gen_random_uuid(),
  questionnaire_id text references questionnaires(id),
  user_id uuid null,
  client_id text,
  mode q_mode,
  status q_status default 'draft',
  current_ord int default 0,
  created_at timestamptz,
  updated_at timestamptz
);

create table if not exists answers (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid references submissions(id),
  question_key text,
  value jsonb not null,
  answered_at timestamptz default now()
);

create table if not exists mode_cooldowns (
  id uuid primary key default gen_random_uuid(),
  user_id uuid null,
  client_id text null,
  mode q_mode,
  hidden_until timestamptz,
  created_at timestamptz default now()
);