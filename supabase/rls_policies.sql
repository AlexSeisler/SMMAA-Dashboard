-- Enable RLS
alter table clients enable row level security;
alter table tasks enable row level security;
alter table files enable row level security;

-- Clients: only see your own row
create policy "Client can view own profile"
  on clients for select
  using (auth.uid()::text = id);

-- Tasks: only see rows for your client_id
create policy "Client can read own tasks"
  on tasks for select
  using (client_id = current_setting('request.jwt.claim.client_id', true));

-- Files: only see files for your client_id
create policy "Client can read own files"
  on files for select
  using (client_id = current_setting('request.jwt.claim.client_id', true));
