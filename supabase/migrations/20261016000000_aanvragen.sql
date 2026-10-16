-- Aanvragen via het contactformulier van atenergysolutions.nl
create table if not exists public.aanvragen (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  naam        text not null check (char_length(naam) between 2 and 100),
  email       text not null check (char_length(email) <= 160),
  telefoon    text check (char_length(telefoon) <= 30),
  postcode    text not null check (char_length(postcode) <= 8),
  type        text not null default 'particulier' check (type in ('particulier', 'zakelijk')),
  interesse   text[] not null default '{}',
  bericht     text not null check (char_length(bericht) between 10 and 3000),
  status      text not null default 'nieuw' check (status in ('nieuw', 'in_behandeling', 'offerte_verstuurd', 'afgerond', 'afgewezen')),
  bron        text not null default 'website',
  omgeving    text not null default 'production'
);

comment on table public.aanvragen is 'Offerte-aanvragen via het websiteformulier. Alleen toegankelijk via de server (service role).';
create index if not exists aanvragen_created_at_idx on public.aanvragen (created_at desc);
create index if not exists aanvragen_status_idx on public.aanvragen (status);

-- Beveiliging: RLS aan en géén policies => niet leesbaar/schrijfbaar met de publieke sleutel.
alter table public.aanvragen enable row level security;
revoke all on public.aanvragen from anon, authenticated;
