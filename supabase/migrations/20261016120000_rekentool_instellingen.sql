-- Prijzen en modellen van de rekentool. Alleen via de server (api/rekentool) te lezen en te schrijven.
create table if not exists public.rekentool_instellingen (
  id          smallint primary key default 1 check (id = 1),
  config      jsonb not null,
  updated_at  timestamptz not null default now()
);
alter table public.rekentool_instellingen enable row level security;
revoke all on public.rekentool_instellingen from anon, authenticated;
