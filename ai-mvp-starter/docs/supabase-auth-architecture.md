# Supabase 인증 아키텍처 — `auth.users`, `public.users`, RLS, 트리거

> Supabase를 처음 쓸 때 가장 헷갈리는 지점: "왜 `users` 테이블이 두 개 있지?", "RLS를 안 켜도 로그인은 되던데?", "setup.sql은 뭘 하는 거지?" 이 세 질문에 대한 정리. 프로젝트 독립적.

---

## 1. 왜 `users` 테이블이 두 개 있나

Supabase는 **인증(auth)** 과 **비즈니스(app)** 를 의도적으로 분리한다.

### `auth.users` — Supabase가 관리 (건드리지 말 것)

```
auth.users
├── id                    (UUID) 인증 아이덴티티
├── email
├── encrypted_password    비밀번호 해시
├── email_confirmed_at
├── last_sign_in_at
├── raw_app_meta_data     { provider: "google", ... }
├── raw_user_meta_data    OAuth 프로필 (이름, 아바타 등)
└── ... (MFA, refresh token 등 수십 개)
```

- `supabase.auth.signUp()`, `signInWithPassword()` 등 **Auth API가 자동으로 채움**
- 민감 데이터(비밀번호 해시, refresh token)가 있어서 기본적으로 **외부 접근 차단**
- Supabase가 새 기능 추가할 때 여기 컬럼/테이블을 추가 → 사용자가 건드리면 버전 업그레이드 시 충돌

### `public.users` — 내 앱이 관리

```
public.users
├── id          (UUID) ← auth.users.id와 동일한 값
├── email
├── name
├── avatar_url
├── subscription_tier
└── ... (비즈니스 필드)
```

- Drizzle/Prisma 등 **ORM으로 자유롭게 정의**
- 다른 테이블에서 FK로 참조 (`posts.author_id → public.users.id`)
- 공개된 표면 — 앱이 직접 읽고 쓰는 데이터

### 왜 분리하나 — 3가지 이유

1. **Supabase의 `auth` 스키마는 수정 불가 영역**
   - `alter table auth.users add column subscription_tier text;` → Supabase 업데이트 시 충돌
   - 비즈니스 컬럼은 반드시 `public`에 분리
2. **보안 경계 분리**
   - `auth.users`는 비밀번호 해시/토큰이 있는 금고
   - `public.users`는 앱이 일상적으로 접근하는 공개 표면
3. **FK 관계 설정의 안정성**
   - `auth.users`를 직접 FK로 걸면 Supabase 스키마 변경 시 파괴적 영향
   - `public.users`를 중간에 둬서 버퍼 역할

---

## 2. 두 테이블을 잇는 트리거

### 문제: 기본 상태에선 두 테이블이 연결 안 됨

회원가입만 하면:
```
signUp() → auth.users에 행 생성 ✅
         → public.users는 그대로 비어있음 ❌
```

이 상태에서 `posts.author_id`처럼 `public.users`를 참조하는 FK가 있으면 **글 작성 시 FK 위반 에러**.

### 해결: `security definer` 트리거로 자동 복제

Supabase 공식 권장 패턴:

```sql
-- 1. 복제 함수 정의 (슈퍼유저 권한으로 실행)
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer                    -- 핵심: RLS와 권한 체크 우회
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

-- 2. auth.users 삽입 시 자동 발동
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

### 동작 흐름

```
유저가 signUp()
      ↓
Supabase Auth API가 auth.users에 INSERT
      ↓
트리거 on_auth_user_created 발동
      ↓
handle_new_user() 실행 (security definer → RLS 우회)
      ↓
public.users에도 같은 id로 행 생성
      ↓
이제 posts 같은 테이블이 author_id로 이 유저를 FK 참조 가능
```

### `security definer` 의 의미

- 기본값(`security invoker`): 함수를 **호출한 사용자 권한**으로 실행
- `security definer`: 함수를 **정의한 사용자(DB 소유자)** 권한으로 실행
- 트리거는 anon 키로 호출되는 signUp 경로에서도 발동돼야 하므로, 권한 우회가 필수

---

## 3. RLS (Row Level Security) 의 실제 효과

### RLS를 켠다는 게 무슨 의미인가

PostgreSQL 기능. 테이블의 **행 단위 접근 권한**을 선언적으로 정의.

```sql
alter table users enable row level security;
-- 정책(policy)을 하나도 만들지 않음
```

이 상태의 규칙: **"정책 없음 = 전면 거부"**. anon 및 일반 사용자는 SELECT/INSERT/UPDATE/DELETE 모두 차단됨. 쿼리를 날려도 에러 없이 **빈 결과를 받음**.

### 누가 RLS를 우회할 수 있나

| 접근 방식 | RLS 우회? |
|---|---|
| `anon` 키 (브라우저 공개) | ❌ 차단 |
| `authenticated` 역할 (로그인한 유저) | ❌ 차단 (정책 없으면) |
| `service_role` 키 | ✅ 자동 우회 |
| `security definer` 함수 | ✅ 함수 정의자 권한으로 실행 |
| DB 직접 커넥션 (`postgres` 역할) | ✅ 슈퍼유저 |

앱의 서버(Route Handler 등)는 `service_role` 기반 커넥션으로 DB에 접근 → RLS 영향 없음. RLS는 **외부에서 anon 키로 PostgREST API를 직접 호출하는 공격자**를 막는 안전망 역할만 함.

---

## 4. "RLS 안 해도 로그인은 되던데?" — 맞습니다

로그인/회원가입은 RLS와 무관하게 동작한다. 이유:

1. **로그인 자체는 `auth.users` 영역**
   - Supabase Auth API 서버가 auth 스키마에서 처리
   - 우리가 `public`에 건 RLS는 여기 적용 안 됨
2. **트리거는 `security definer`로 RLS 우회**
   - 슈퍼유저 권한으로 실행되므로 `public.users`에 INSERT 가능
3. **앱의 DB 쿼리는 `service_role` 기반**
   - RLS를 자동 우회

### 시나리오별 결과

| 상태 | 회원가입 | 로그인 | 글 작성 | anon 키로 DB 직접 조회 |
|---|---|---|---|---|
| **setup.sql 미실행** | ✅ | ✅ | ❌ FK 에러 | 🚨 **전체 데이터 털림** |
| **트리거만 실행** | ✅ | ✅ | ✅ | 🚨 **여전히 털림** |
| **RLS만 실행 (트리거 없음)** | ✅ | ✅ | ❌ FK 에러 | ✅ 차단 |
| **둘 다 실행 (정상)** | ✅ | ✅ | ✅ | ✅ 차단 |

즉:
- **앱 작동**에 필요한 건 **트리거**
- **데이터 보호**에 필요한 건 **RLS**
- 둘은 독립적이고 서로 대체 불가

---

## 5. RLS 없이 배포하면 벌어지는 일 — 공격 시나리오

`NEXT_PUBLIC_SUPABASE_ANON_KEY`는 브라우저 번들에 포함되므로 **누구나 볼 수 있는 공개키**다. 공격자가 이 키를 획득하는 건 아무 JS 앱의 Network 탭만 열면 된다.

### RLS 없을 때 — 터미널에서 그대로 실행

```bash
# 모든 유저 조회
curl 'https://xxx.supabase.co/rest/v1/users?select=*' \
  -H "apikey: sb_publishable_xxx"
# → 전체 이메일 목록, 가입일 등 그대로 노출

# 비공개 글 전부 조회
curl 'https://xxx.supabase.co/rest/v1/posts?select=*' \
  -H "apikey: sb_publishable_xxx"
# → 초안/비공개 글까지 읽힘

# 아무 유저 이름으로 글 쓰기 / 삭제
curl -X POST 'https://xxx.supabase.co/rest/v1/posts' \
  -H "apikey: sb_publishable_xxx" \
  -d '{"author_id": "victim-user-uuid", "title": "fake"}'
# → 앱을 거치지 않고 바로 DB에 쓰기 성공
```

앱 레이어의 인가 체크를 **완전히 우회**한다.

### RLS 있을 때

```bash
curl 'https://xxx.supabase.co/rest/v1/users?select=*' \
  -H "apikey: sb_publishable_xxx"
# → []     (빈 배열, 정책 없으니 모두 거부)
```

앱은 `service_role`로 정상 동작하고, 외부만 막힌다.

### 결론

**RLS는 "옵션"이 아니라 "기본"으로 간주하라.** 껐을 때의 편의성 이득은 없고, 켜더라도 앱 동작에 영향이 없다. 비용 0, 효과 100%.

---

## 6. 실행 순서 — 왜 마이그레이션 **후**에 setup.sql을 돌리나

setup.sql은 **이미 존재하는 테이블**을 수정한다:

```sql
alter table users enable row level security;  -- users 테이블이 있어야 함
alter table posts enable row level security;  -- posts 테이블이 있어야 함

-- 트리거 함수 안에서 public.users에 INSERT
insert into public.users (id, email, name) values (...);
```

테이블이 없는 상태에서 실행하면 `relation "users" does not exist` 에러. 따라서:

```
① 스키마 정의 (ORM) → ② 마이그레이션 실행 → ③ setup.sql 실행
                         (테이블 생성)         (RLS + 트리거)
```

### 왜 마이그레이션에 합치지 않나

1. **ORM의 관할 영역 밖**
   - Drizzle/Prisma는 `schema.ts` 또는 `schema.prisma`의 테이블 정의만 SQL로 변환
   - RLS, PL/pgSQL 함수, `auth.users` 트리거 같은 Supabase 전용 기능은 표현 불가
2. **`auth` 스키마 참조 불가**
   - ORM은 `public` 스키마만 추적
   - `auth.users`에 트리거 거는 SQL을 마이그레이션에 넣을 방법이 없음
3. **관심사 분리**
   - 마이그레이션: 스키마 진화 이력 (여러 번 실행)
   - setup.sql: 최초 1회 설정 (트리거/RLS는 보통 안 바뀜)
   - 멱등성(idempotent)을 보장하면 setup.sql은 여러 번 실행해도 안전

### setup.sql의 멱등성 패턴

```sql
-- 재실행 가능하게
drop trigger if exists on_auth_user_created on auth.users;
create or replace function public.handle_new_user() ...
alter table users enable row level security;  -- 이미 켜져있으면 no-op
```

---

## 7. 체크리스트 — 신규 Supabase 프로젝트 시작 시

인증이 제대로 돌아가려면:

- [ ] `schema.ts` 등 ORM 스키마에 `public.users` 테이블 정의 (id는 UUID, `auth.users.id`와 매칭)
- [ ] 스키마 마이그레이션 실행 → `public.users`, `public.posts` 등 생성
- [ ] Supabase Dashboard의 SQL Editor에서 setup.sql 실행
  - [ ] RLS 활성화 (`alter table ... enable row level security`)
  - [ ] `handle_new_user()` 함수 정의 (`security definer`)
  - [ ] `on_auth_user_created` 트리거 생성
- [ ] 회원가입 테스트 → `auth.users`와 `public.users` 양쪽에 같은 id로 행 생성되는지 확인
- [ ] (선택) anon 키로 외부에서 `/rest/v1/users` 호출해서 빈 배열 반환되는지 검증

---

## 8. 한 줄 요약

> **인증은 `auth.users`, 비즈니스 데이터는 `public.users`. 회원가입 시 `security definer` 트리거가 두 테이블을 `id`로 잇는다. RLS는 앱 동작과 무관하지만, 안 켜면 `anon` 키로 누구나 DB를 직접 털 수 있으니 반드시 켠다.**
