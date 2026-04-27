-- ================================================================
-- Supabase 초기 설정 SQL
-- Dashboard → SQL Editor에서 1회 실행
-- ================================================================

-- RLS "안전망" 활성화 — 정책 없음 = 기본 deny.
-- Service Role Key를 사용하는 서버만 접근 가능.
-- anon key(브라우저)로는 아무것도 못 읽음.
alter table users enable row level security;

-- ================================================================
-- Supabase Auth → users 테이블 자동 동기화 트리거
-- ================================================================
-- 사용자가 회원가입하면 auth.users에 행이 추가되는데,
-- 그걸 public.users에도 자동 복제해서 Drizzle이 쓸 수 있게 함.

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.users (id, email, name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1))
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
