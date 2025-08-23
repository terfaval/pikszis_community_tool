create extension if not exists "pgcrypto";

do $$ begin
  create type user_role as enum ('guest','user','moderator','admin');
exception
  when duplicate_object then null;
end $$;

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text not null,
  display_name text not null,
  created_at timestamptz default now()
);

create table if not exists public.profiles (
  id uuid primary key,
  email text unique,
  display_name text,
  role user_role not null default 'user',
  mfa_enforced boolean not null default false,
  last_login_at timestamptz,
  last_seen_at timestamptz,
  consent_terms_at timestamptz,
  consent_privacy_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint fk_profiles_user foreign key (id) references public.users(id) on delete cascade
);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (new.id, new.email, new.display_name);
  return new;
end;
$$;

do $$ begin
  create trigger on_user_created
  after insert on public.users
  for each row execute procedure public.handle_new_user();
exception
  when duplicate_object then null;
end $$;

create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'admin'
  );
$$;

create or replace function public.set_admin(uid uuid, enabled boolean)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  update public.profiles
  set role = case when enabled then 'admin' else 'user' end
  where id = uid;
end;
$$;

alter table public.profiles enable row level security;

do $$ begin
  create policy "Select own profile" on public.profiles
    for select using (auth.uid() = id);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy "Update own profile" on public.profiles
    for update using (auth.uid() = id);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy "Admin select profiles" on public.profiles
    for select using (is_admin());
exception when duplicate_object then null; end $$;

do $$ begin
  create policy "Admin update profiles" on public.profiles
    for update using (is_admin());
exception when duplicate_object then null; end $$;
