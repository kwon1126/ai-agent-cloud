# Next.js + Supabase + Drizzle 스택 실전 노트

> 이 문서는 **Next.js App Router + Supabase + Drizzle** 스택으로 신규 프로젝트를 시작할 때 실제로 겪는 선택/함정/해결 방법을 일반론 수준으로 정리한 것이다. 특정 프로젝트의 규칙(RLS 사용 여부, 폴더 구조 등)이 아니라, 같은 스택이면 누구나 마주치는 공통 이슈만 다룬다.

---

## 1. 패키지 매니저 선택

### 2026년 현재 우선순위

1. **pnpm** — 디스크 효율(심볼릭 링크로 중복 제거), 설치 속도, 모노레포 기본 지원. Next.js 공식 권장.
2. **npm** — Node 기본 내장. 개인 프로젝트/튜토리얼 용도. v10+에서 속도 개선됨.
3. **Bun** — 설치/런타임 모두 빠름. 프로덕션 검증 진행 중이라 신규 프로젝트에만 신중히 도입.
4. **Yarn** — Yarn Classic은 레거시, Yarn Berry PnP는 호환성 이슈로 점유율 하락.

### pnpm 설치 (Node 16.13+)

```bash
corepack enable
corepack prepare pnpm@latest --activate
```

Node.js에 기본 포함된 `corepack`이 `package.json`의 `packageManager` 필드를 읽어 올바른 버전을 자동 설치한다. 별도 설치 불필요.

### 모노레포 지원의 실제 의미

> 하나의 Git 저장소에 여러 패키지(apps/web, apps/mobile, packages/ui 등)를 담는 구조.

`pnpm-workspace.yaml` 한 파일로 묶이고, 내부 패키지를 `"dependencies": { "@org/ui": "workspace:*" }` 형태로 **npm 배포 없이 직접 참조** 가능. 수정하면 즉시 반영. 의존성 중복도 자동 제거.

---

## 2. Lint & Format — Biome 일원화

### 왜 Prettier + ESLint를 안 쓰나

- Prettier(포맷) + ESLint(린트) 조합은 **설정 파일 2~4개 + plugin 다수 + peer dep 지옥**.
- Next.js 16+에서 `next lint`는 deprecated — 사용자가 직접 ESLint 9 Flat Config를 세팅해야 한다.
- **Biome는 Rust 기반** (25배+ 빠름) + **설정 파일 1개**(`biome.json`) + Prettier 기본값과 97% 호환.

### 설치

```bash
pnpm add -D @biomejs/biome
```

### 최소 `biome.json`

```json
{
  "$schema": "https://biomejs.dev/schemas/2.4.12/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": {
    "includes": ["**", "!.next", "!node_modules", "!dist", "!**/migrations/**"]
  },
  "formatter": { "indentStyle": "space", "indentWidth": 2, "lineWidth": 100 },
  "linter": { "rules": { "recommended": true } },
  "javascript": {
    "formatter": { "quoteStyle": "double", "semicolons": "always", "trailingCommas": "all" }
  }
}
```

### 스크립트

```json
"lint": "biome check",
"lint:fix": "biome check --write",
"format": "biome format --write"
```

### 자주 끄게 되는 규칙

프로젝트 성격에 따라 꺼야 할 수 있다. 예시:

| 규칙 | 끄는 이유 |
|---|---|
| `style/noNonNullAssertion` | `process.env.X!` 패턴을 많이 쓸 때 |
| `suspicious/useIterableCallbackReturn` | Supabase 쿠키 `forEach(x => set(...))` 패턴 허용 |
| `suspicious/noShadowRestrictedNames` (for `error.tsx`) | Next.js 예약 파일명 충돌 무시 |

---

## 3. Supabase 프로젝트 & 새 API 키 포맷

### 2025년 키 시스템 교체

Supabase가 JWT(`eyJ...`) 방식에서 **prefix 방식**으로 전환했다. 구 프로젝트는 기존 JWT가 유지되지만, 신규 프로젝트는 아래 포맷.

| 구 포맷 (JWT) | 신 포맷 (prefix) | 역할 |
|---|---|---|
| `anon public` (`eyJ...`) | `sb_publishable_*` | 브라우저/서버 양쪽 OK |
| `service_role` (`eyJ...`) | `sb_secret_*` | **서버 전용**, 관리자 권한 |

`@supabase/ssr`와 `@supabase/supabase-js`는 두 포맷 모두 지원 — 코드 변경 불필요. 값만 바꾸면 됨.

### 키 복사 체크리스트

- **Publishable/Anon 키**: 그대로 복사. `.env`의 `NEXT_PUBLIC_SUPABASE_ANON_KEY`에 붙여넣기.
- **Secret/Service role 키**: 기본적으로 가려져 있음. 눈 👁️ 아이콘 클릭 → 복사 버튼 사용. **수동 드래그 복사 시 잘려나감** (실제로 많이 겪는 실수).
- Git 커밋 방지: `.env*.local`이 `.gitignore`에 포함돼 있는지 확인 (Next.js는 기본 포함).

---

## 4. DB 연결 — Pooler vs Direct (가장 큰 함정)

### Supabase Dashboard의 3가지 연결 탭

| 탭 | 포트 | 호스트 형식 | 용도 |
|---|---|---|---|
| **Transaction pooler** | 6543 | `aws-N-<region>.pooler.supabase.com` | 앱 런타임 (서버리스 필수) |
| **Session pooler** | 5432 | `aws-N-<region>.pooler.supabase.com` | 마이그레이션, 긴 트랜잭션 |
| **Direct connection** | 5432 | `db.<projectref>.supabase.co` | ⚠️ **IPv6 전용** |

### 핵심 함정: Direct connection의 IPv6 문제

`db.<projectref>.supabase.co`는 2024년부터 **무료 플랜에서 IPv4 주소를 제공하지 않는다**. 가정/사무실 네트워크 대부분이 IPv6 end-to-end를 지원하지 않기 때문에 다음 에러가 발생한다:

```
Error: getaddrinfo ENOTFOUND db.xxxxx.supabase.co
```

**해결**: 마이그레이션용 URL(`DIRECT_URL`)에도 **Session pooler(5432)** 를 쓴다. `DATABASE_URL`(Transaction pooler 6543)과 **호스트가 완전히 동일**하고 **포트만 다르다**.

### 포트 5432가 방화벽에 막힌 경우

일부 기업/VPN 환경은 5432를 차단하고 6543만 허용한다. 그럴 땐 `DIRECT_URL`도 6543을 쓴다 (Transaction pooler로 마이그레이션).

단, Transaction pooler는 **세션 상태가 없어서** 아래 작업이 실패할 수 있다:
- `CREATE INDEX CONCURRENTLY` (트랜잭션 밖 실행)
- Advisory lock 기반 마이그레이션
- 일부 postgres.js prepared statement

기본 CRUD 스키마 생성은 문제없음. 더 복잡한 작업이 필요하면 **Supabase Dashboard의 SQL Editor에서 직접 실행**(HTTPS 443만 쓰므로 어떤 네트워크에서도 작동).

### 비밀번호 URL 인코딩

비밀번호에 특수문자가 있으면 URL 인코딩 필수:

| 문자 | 인코딩 |
|---|---|
| `@` | `%40` |
| `#` | `%23` |
| `&` | `%26` |
| `:` | `%3A` |

---

## 5. Drizzle 마이그레이션 3단계

### 기본 흐름

```
① schema.ts 작성/수정
      ↓
② drizzle-kit generate   ← 로컬에만 SQL 파일 생성 (DB 안 건드림)
      ↓
[생성된 SQL 검토 — 권장]
      ↓
③ drizzle-kit migrate    ← 원격 DB에 적용 + __drizzle_migrations에 이력 저장
```

### 두 명령의 구분

| 명령 | 하는 일 | DB 건드림? |
|---|---|---|
| `drizzle-kit generate` | `schema.ts` diff → SQL 파일 생성 | ❌ |
| `drizzle-kit migrate` | `migrations/` 폴더의 SQL 실행 | ✅ |
| `drizzle-kit push` | **스키마를 직접 푸시, 이력 없음** | ✅ **쓰지 말 것** |

> **`db:push` 금지 이유**: 이력이 남지 않아 배포 환경 동기화가 깨진다. 로컬 DB에는 적용됐는데 프로덕션은 안 된 상태 추적 불가.

### Drizzle이 못 하는 것 — Supabase `auth` 스키마

`drizzle-kit migrate`는 `schema.ts`에 정의된 테이블만 건드린다. Supabase가 관리하는 `auth.users`, `auth.sessions` 등은 **범위 밖**. 따라서 다음은 별도로 처리해야 한다:

- RLS 정책 생성/수정
- `auth.users` → `public.users` 동기화 트리거
- Custom extensions, functions

해결 2가지:

**A. Dashboard SQL Editor 수동 실행 (1회성)**
- 프로젝트 루트에 `setup.sql` 같은 파일을 만들어 커밋
- Dashboard → SQL Editor → 붙여넣기 → Run

**B. 코드로 실행 (반복 가능, idempotent 하게)**

```typescript
// scripts/apply-setup.ts
import postgres from "postgres";
import fs from "node:fs";
import "dotenv/config";

const sql = postgres(process.env.DIRECT_URL!, { max: 1 });
await sql.unsafe(fs.readFileSync("./src/db/setup.sql", "utf-8"));
await sql.end();
```

```bash
pnpm tsx scripts/apply-setup.ts
```

SQL은 반드시 **idempotent**하게 작성 (`create or replace function`, `drop trigger if exists` 등).

---

## 6. Next.js + Supabase 인증 아키텍처

### 핵심 원리: 쿠키 + Middleware 기반 세션

```
로그인 성공
    ↓
Supabase가 Set-Cookie 헤더로 JWT + refresh token 저장
    ↓
매 요청마다 middleware.ts가 실행
    ↓
updateSession() → supabase.auth.getUser() → 토큰 만료 임박 시 refresh
    ↓
Server Component / Route Handler에서 createClient() 호출
    ↓
요청 쿠키 → Supabase 서버에 검증 요청 → user 반환 (or null)
```

### `@supabase/ssr`의 클라이언트 3종

| 용도 | 생성 함수 | 차이점 |
|---|---|---|
| Client Component | `createBrowserClient` | `document.cookie` 사용 |
| Server Component / Route Handler | `createServerClient` + `next/headers#cookies` | 읽기 전용 컨텍스트에서도 동작 |
| Middleware | `createServerClient` + `NextRequest.cookies` | response에 Set-Cookie 주입 가능 |

세 개를 섞어 쓰면 쿠키 갱신이 안 되거나 세션이 터진다. **반드시 컨텍스트별로 분리**.

### `getUser()` vs `getSession()` — 서버에서 반드시 `getUser()`

```typescript
// ❌ 위험 — 쿠키값을 검증 없이 디코딩
const { data: { session } } = await supabase.auth.getSession();

// ✅ 안전 — Supabase 서버가 JWT 서명 검증
const { data: { user } } = await supabase.auth.getUser();
```

공격자가 쿠키를 위조하면 `getSession()`은 속지만 `getUser()`는 검증에서 걸러낸다. **Route Handler의 인가 체크는 반드시 `getUser()`**.

### 재사용 헬퍼 패턴

```typescript
// lib/auth.ts
export async function getCurrentUser() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  return user;
}

export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  return user;
}
```

사용처:
- **UI 분기** (로그인/로그아웃 버튼 등): `getCurrentUser()` + null 체크
- **보호 페이지**: `requireUser()` — 자동 리다이렉트
- **변경 API(POST/PATCH/DELETE)**: `getCurrentUser()` → null이면 401 반환

---

## 7. 이메일 인증 — 개발 단계에선 꺼두기

Supabase는 기본값으로 회원가입 후 **이메일 링크 확인 필수**다. 확인 전에 로그인 시도하면:

```
{ code: "email_not_confirmed", message: "Email not confirmed" }
```

### 해결 3가지

| 상황 | 방법 |
|---|---|
| 지금 이 유저 하나만 | Dashboard → Authentication → Users → 해당 행 → **Confirm user** |
| 개발 내내 편하게 | Dashboard → Authentication → Providers → Email → **Confirm email OFF** |
| 배포 직전 | Confirm email을 **다시 ON** (스팸 유저 차단) |

---

## 8. 자주 겪는 에러 맵

| 에러 | 원인 | 해결 |
|---|---|---|
| `ENOTFOUND db.xxxxx.supabase.co` | Direct connection 호스트 사용 (IPv6 전용) | Session pooler로 교체 |
| `Tenant or user not found` | `postgres.xxxxx` username 부분 오타 | Dashboard에서 정확히 복사 |
| `password authentication failed` | 비밀번호 URL 인코딩 누락 or 오타 | 특수문자 인코딩, 모르면 비밀번호 재설정 |
| `email_not_confirmed` | 이메일 인증 미완료 | §7 참조 |
| `prepared statement "xxx" already exists` | Transaction pooler에 postgres.js가 prepared statement 사용 | `prepare: false` 옵션, 또는 Session pooler 사용 |
| `relation "xxx" does not exist` (setup.sql 실행 시) | 마이그레이션 전에 setup.sql 실행함 | **migrate → setup.sql** 순서 지키기 |
| 환경변수 변경 반영 안 됨 | Next.js는 `.env`를 빌드/서버 시작 시에만 로드 | dev 서버 재시작 |

---

## 9. 배포 (Vercel 기준)

### 환경변수 6종 (Vercel Dashboard → Settings → Environment Variables)

```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
DATABASE_URL    (Transaction pooler, 6543)
DIRECT_URL      (Session pooler, 5432)
```

### `build` 스크립트에 마이그레이션 포함

```json
"build": "drizzle-kit migrate && next build"
```

이 패턴이면:
- 로컬에서 `drizzle-kit generate`로 SQL 파일 커밋
- Vercel이 빌드 시 자동으로 `drizzle-kit migrate` 실행
- 프로덕션 DB가 항상 최신 스키마와 동기화

**주의**: 실패 시 빌드 전체가 실패하도록 `&&` 사용. Vercel 빌드 로그에서 어느 단계에서 실패했는지 즉시 확인 가능.

---

## 10. 체크리스트 — 신규 프로젝트 시작 시

- [ ] pnpm 설치 (`corepack enable`)
- [ ] Biome 세팅 (`pnpm add -D @biomejs/biome` + `biome.json`)
- [ ] Supabase 프로젝트 생성 → API 키 + DB Connection string 복사
- [ ] `.env`에 6개 값 입력 — **`DIRECT_URL`은 Session pooler(5432)**
- [ ] `drizzle-kit generate` → 생성된 SQL 검토 → `drizzle-kit migrate`
- [ ] Dashboard SQL Editor에서 RLS/트리거 등 `setup.sql` 실행
- [ ] Dashboard → Auth → Email provider의 **Confirm email** 개발 중엔 OFF
- [ ] `middleware.ts`로 세션 자동 갱신 구성
- [ ] `lib/auth.ts`에 `getCurrentUser` / `requireUser` 헬퍼 작성
- [ ] 서버 어디서든 인가 체크는 `getUser()` 기반 (절대 `getSession()` 아님)
- [ ] `.gitignore`에 `.env*.local` 포함 확인
- [ ] `build` 스크립트에 `drizzle-kit migrate` 포함
