-- Kør i Supabase SQL Editor. Opret brugere i Authentication først.
create extension if not exists pgcrypto;
create table if not exists public.staff (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null check (length(trim(name)) between 1 and 100),
  role text not null default 'employee' check (role in ('admin','employee')),
  can_waiter boolean not null default true,
  can_dishwasher boolean not null default true,
  active boolean not null default true
);
create table if not exists public.shifts (
  id uuid primary key default gen_random_uuid(),
  shift_day date not null,
  start_time time not null,
  end_time time not null,
  position text not null check (position in ('Tjener','Opvasker')),
  employee_id uuid references public.staff(id),
  published boolean not null default false,
  offered boolean not null default false,
  locked boolean not null default false,
  notes text not null default '',
  created_at timestamptz not null default now(),
  constraint valid_hours check (start_time >= time '07:00' and (end_time <= time '23:59:59' or end_time = time '00:00')),
  constraint positive_shift check (start_time < end_time or end_time = time '00:00'),
  constraint no_locked_offer check (not (locked and offered))
);
-- end_time 00:00 means midnight at the END of shift_day.
create table if not exists public.unavailability (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid not null references public.staff(id) on delete cascade,
  day date not null,
  note text not null default '',
  unique(employee_id,day)
);
create table if not exists public.settings (
  id integer primary key default 1 check(id=1),
  wishes_deadline date
);
insert into public.settings (id) values (1) on conflict do nothing;
create table if not exists public.shift_log (
  id bigint generated always as identity primary key,
  shift_id uuid not null,
  actor_id uuid not null,
  old_employee_id uuid,
  new_employee_id uuid,
  action text not null,
  created_at timestamptz not null default now()
);
create or replace function public.is_admin() returns boolean language sql stable security definer set search_path = '' as $$
 select exists(select 1 from public.staff where id=(select auth.uid()) and role='admin' and active);
$$;
revoke all on function public.is_admin() from public, anon;
grant execute on function public.is_admin() to authenticated;

alter table public.staff enable row level security;
alter table public.shifts enable row level security;
alter table public.unavailability enable row level security;
alter table public.settings enable row level security;
alter table public.shift_log enable row level security;

create policy "staff read" on public.staff for select to authenticated using (true);
create policy "staff admin insert" on public.staff for insert to authenticated with check (public.is_admin());
create policy "staff admin update" on public.staff for update to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "staff admin delete" on public.staff for delete to authenticated using (public.is_admin());
create policy "shifts read" on public.shifts for select to authenticated using (published or public.is_admin());
create policy "shifts admin insert" on public.shifts for insert to authenticated with check (public.is_admin());
create policy "shifts admin update" on public.shifts for update to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "shifts admin delete" on public.shifts for delete to authenticated using (public.is_admin());
create policy "wishes read" on public.unavailability for select to authenticated using (employee_id=auth.uid() or public.is_admin());
create policy "wishes insert" on public.unavailability for insert to authenticated with check (employee_id=auth.uid() and (select wishes_deadline from public.settings where id=1) >= current_date);
create policy "wishes delete" on public.unavailability for delete to authenticated using (public.is_admin() or (employee_id=auth.uid() and (select wishes_deadline from public.settings where id=1) >= current_date));
create policy "settings read" on public.settings for select to authenticated using (true);
create policy "settings update" on public.settings for update to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "log read" on public.shift_log for select to authenticated using (public.is_admin() or old_employee_id=auth.uid() or new_employee_id=auth.uid());

-- Atomiske handlinger: vagten skifter først ejer når en anden overtager den.
create or replace function public.offer_my_shift(p_shift uuid) returns void
language plpgsql security definer set search_path='' as $$
begin
 update public.shifts set offered=true
 where id=p_shift and employee_id=auth.uid() and published and not locked and not offered;
 if not found then raise exception 'Vagten kan ikke udbydes'; end if;
 insert into public.shift_log(shift_id,actor_id,old_employee_id,new_employee_id,action)
 values(p_shift,auth.uid(),auth.uid(),auth.uid(),'offered');
end; $$;
create or replace function public.cancel_my_offer(p_shift uuid) returns void
language plpgsql security definer set search_path='' as $$
begin
 update public.shifts set offered=false where id=p_shift and employee_id=auth.uid() and offered and not locked;
 if not found then raise exception 'Tilbuddet kan ikke annulleres'; end if;
end; $$;
create or replace function public.claim_shift(p_shift uuid) returns void
language plpgsql security definer set search_path='' as $$
declare v_old uuid; v_position text; v_day date; v_start time; v_end time;
begin
 select employee_id,position,shift_day,start_time,end_time into v_old,v_position,v_day,v_start,v_end
 from public.shifts where id=p_shift and published and offered and not locked for update;
 if not found then raise exception 'Vagten er ikke længere ledig'; end if;
 if v_old=auth.uid() then raise exception 'Du har allerede vagten'; end if;
 if not exists(select 1 from public.staff where id=auth.uid() and active and
 (case when v_position='Tjener' then can_waiter else can_dishwasher end)) then
 raise exception 'Du har ikke adgang til denne vagttype'; end if;
 if exists(select 1 from public.shifts where employee_id=auth.uid() and published and shift_day=v_day and id<>p_shift
   and (start_time < (case when v_end=time '00:00' then time '23:59:59' else v_end end))
   and (end_time=time '00:00' or end_time>v_start)) then
 raise exception 'Du har en overlappende vagt'; end if;
 update public.shifts set employee_id=auth.uid(),offered=false where id=p_shift;
 insert into public.shift_log(shift_id,actor_id,old_employee_id,new_employee_id,action)
 values(p_shift,auth.uid(),v_old,auth.uid(),'claimed');
end; $$;
revoke all on function public.offer_my_shift(uuid),public.cancel_my_offer(uuid),public.claim_shift(uuid) from public,anon;
grant execute on function public.offer_my_shift(uuid),public.cancel_my_offer(uuid),public.claim_shift(uuid) to authenticated;

-- Første admin: Opret personen i Authentication > Users, og kør så:
-- insert into public.staff(id,name,role) values ('BRUGER-UUID','Administrator','admin');
-- Første admin kan oprettes via SQL-editoren (der kører som databaseejer).
-- Alle øvrige medarbejdere oprettes i Authentication > Users og tilføjes i appens administration.
