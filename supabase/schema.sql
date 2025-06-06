-- CLIENTS TABLE
create table if not exists clients (
  id text primary key,
  name text not null,
  status text default 'active'
);

-- TASKS TABLE
create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  client_id text references clients(id) on delete cascade,
  task text not null,
  status text default 'to_do',
  priority text default 'medium',
  due date,
  created_by text,
  inserted_at timestamp with time zone default timezone('utc', now())
);

-- FILES TABLE
create table if not exists files (
  id uuid primary key default gen_random_uuid(),
  task_id uuid references tasks(id) on delete cascade,
  client_id text references clients(id) on delete cascade,
  file_url text not null,
  status text default 'uploaded',
  inserted_at timestamp with time zone default timezone('utc', now())
);
