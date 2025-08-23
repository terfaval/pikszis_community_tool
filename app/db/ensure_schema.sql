-- enable pgcrypto for gen_random_uuid()
create extension if not exists "pgcrypto";

-- enums ------------------------------------------------------------------
do $$ begin
  create type q_type as enum (
    'likert_1_5',
    'likert_1_4',
    'single_choice',
    'multiple_choice',
    'open_text',
    'other',
    'numeric'
  );
exception
  when duplicate_object then null;
end $$;

do $$ begin
  create type q_status as enum ('draft','submitted');
exception
  when duplicate_object then null;
end $$;

-- bővített enum a kérdőív módokhoz (létrehozza, ha hiányzik, különben hiányzó értékeket ad hozzá)
do $$ begin
  if not exists (select 1 from pg_type where typname = 'q_mode') then
    create type q_mode as enum ('pool', 'idea', 'community', 'targeted', 'ce');
  else
    -- hiányzó értékek hozzáadása
    if not exists (
      select 1 from pg_type t
      join pg_enum e on t.oid = e.enumtypid
      where t.typname = 'q_mode' and e.enumlabel = 'pool'
    ) then
      alter type q_mode add value 'pool';
    end if;
    if not exists (
      select 1 from pg_type t
      join pg_enum e on t.oid = e.enumtypid
      where t.typname = 'q_mode' and e.enumlabel = 'idea'
    ) then
      alter type q_mode add value 'idea';
    end if;
    if not exists (
      select 1 from pg_type t
      join pg_enum e on t.oid = e.enumtypid
      where t.typname = 'q_mode' and e.enumlabel = 'community'
    ) then
      alter type q_mode add value 'community';
    end if;
    if not exists (
      select 1 from pg_type t
      join pg_enum e on t.oid = e.enumtypid
      where t.typname = 'q_mode' and e.enumlabel = 'targeted'
    ) then
      alter type q_mode add value 'targeted';
    end if;
    if not exists (
      select 1 from pg_type t
      join pg_enum e on t.oid = e.enumtypid
      where t.typname = 'q_mode' and e.enumlabel = 'ce'
    ) then
      alter type q_mode add value 'ce';
    end if;
  end if;
end $$;