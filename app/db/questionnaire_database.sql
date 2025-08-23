-- kérdőívek (questionnaires) tábla
create table if not exists questionnaires (
  id text primary key,
  title text not null,
  version text default '1.0.0',
  is_minor_allowed bool,
  requires_guardian_permission_level text default 'general',
  mode q_mode default 'pool',
  question_count int,
  estimated_duration_minutes int,
  intro_text text,
  is_active bool default true,
  created_at timestamptz default now()
);

-- kérdések (questions) tábla
create table if not exists questions (
  id text primary key,
  questionnaire_id text references questionnaires(id),
  priority int default 0,
  title text not null,
  qtype q_type not null,           -- pl. 'likert_1_5', 'open_text', 'single_choice', 'numeric'
  random_order bool default false,
  ord int,
  branch_rules jsonb,              -- JSON objektum a válaszopciókkal és az ágat szabályozó logikával
  random_answer bool default false,
  intro_text text,
  created_at timestamptz default now()
);

-- submissions -------------------------------------------------------------
create table if not exists submissions (
  id uuid primary key default gen_random_uuid(),
  questionnaire_id text references questionnaires(id) on delete cascade,
  user_id uuid,
  client_id text,
  mode q_mode not null,
  status q_status not null default 'draft',
  current_ord int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- answers ----------------------------------------------------------------
create table if not exists answers (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid references submissions(id) on delete cascade,
  question_key text,
  value jsonb,
  answered_at timestamptz not null default now()
);

-- mode_cooldowns ---------------------------------------------------------
create table if not exists mode_cooldowns (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  client_id text,
  mode q_mode not null,
  hidden_until timestamptz not null,
  created_at timestamptz not null default now()
);

-- indexes ----------------------------------------------------------------
create index if not exists submissions_user_id_idx on submissions(user_id);
create index if not exists submissions_client_id_idx on submissions(client_id);
create index if not exists answers_submission_id_idx on answers(submission_id);
create index if not exists mode_cooldowns_user_mode_idx on mode_cooldowns(user_id, mode);
create index if not exists mode_cooldowns_client_mode_idx on mode_cooldowns(client_id, mode);

-- questions.id: UUID -> TEXT (ha még nem text)
alter table if exists questions
  drop constraint if exists questions_pkey;

alter table if exists questions
  alter column id type text using id::text;

alter table if exists questions
  add primary key (id);
