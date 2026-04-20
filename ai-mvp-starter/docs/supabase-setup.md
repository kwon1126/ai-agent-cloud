# Supabase 연결 & 마이그레이션 가이드

> 처음부터 끝까지 따라하면 10~15분 안에 `pnpm dev` 화면에서 Supabase에 로그인하고 DB에 글을 쓸 수 있게 됩니다.

---

## 1단계: Supabase 프로젝트 생성

### 1-1. 회원가입 & 프로젝트 만들기

1. [supabase.com](https://supabase.com) 접속 → 우측 상단 **Start your project** 클릭
2. **GitHub 계정으로 로그인** (권장)
3. **New Project** 버튼 클릭
4. 다음 값 입력:

| 항목 | 권장값 |
|---|---|
| **Organization** | 개인은 기본값 사용 |
| **Name** | `ai-mvp-starter` (마음대로) |
| **Database Password** | **강력한 비밀번호 생성 후 별도 저장 ⚠️** (잊어버리면 재설정 필요) |
| **Region** | `Northeast Asia (Seoul)` — 한국 사용자 기준 |
| **Pricing Plan** | Free (2개 프로젝트까지 무료) |

5. **Create new project** → 약 1~2분 프로비저닝 대기

> **⚠️ DB Password 주의**: 이 비밀번호는 `.env.local`에 들어갑니다. 지금 당장 메모해두세요.

---

## 2단계: 필요한 값 6개 복사

프로젝트 대시보드에 진입하면 좌측 사이드바에서 아래 2개 섹션을 방문합니다.

### 2-1. API 키 (3개) — `Project Settings → API`

좌측 하단 **⚙️ Project Settings** → **API** 탭

| 화면 표시 | `.env.local` 변수명 |
|---|---|
| **Project URL** (`https://xxxxx.supabase.co`) | `NEXT_PUBLIC_SUPABASE_URL` |
| **Publishable key** (`sb_publishable_...`) | `NEXT_PUBLIC_SUPABASE_ANON_KEY` |
| **Secret key** (`sb_secret_...`, 눈 아이콘 클릭해서 공개) | `SUPABASE_SERVICE_ROLE_KEY` |

> **2025년 키 포맷 변경**: Supabase가 JWT(`eyJ...`) 방식에서 prefix 방식(`sb_publishable_*` / `sb_secret_*`)으로 교체했습니다. 구 프로젝트는 기존 JWT 키가 그대로 보이며, 둘 다 동일하게 작동합니다.
>
> **🚨 Secret key는 "MySQL root 비밀번호"급 위험**입니다. Git에 커밋하거나 브라우저 번들로 노출되면 DB 전체가 뚫립니다.

### 2-2. DB 연결 문자열 (2개) — `Project Settings → Database`

좌측 하단 **⚙️ Project Settings** → **Database** 탭 → **Connection string** 섹션

오른쪽 상단 탭을 **URI**로 선택한 뒤, 아래 표대로 **두 개를 모두 복사**합니다.

| 탭 선택 | 포트 | `.env.local` 변수명 | 용도 |
|---|---|---|---|
| **Transaction pooler** | `6543` | `DATABASE_URL` | 앱 런타임 (서버리스 필수) |
| **Session pooler** | `5432` | `DIRECT_URL` | 마이그레이션 전용 |

> **⚠️ "Direct connection" 탭은 사용하지 마세요.**
> Dashboard에 Transaction pooler / Session pooler / Direct connection 세 가지가 보이는데, Direct connection(`db.xxxxx.supabase.co`)은 **IPv6 전용**이라 무료 플랜의 일반 가정/사무실 네트워크에서는 `ENOTFOUND` DNS 에러가 납니다. **반드시 Session pooler(`aws-0-*.pooler.supabase.com:5432`)를 선택**하세요.

복사한 문자열에서 **`[YOUR-PASSWORD]` 부분을 1단계에서 저장한 DB 비밀번호로 교체**하세요.

```
# 복사 직후 (비밀번호 자리표시자 포함)
postgresql://postgres.abc...:[YOUR-PASSWORD]@...pooler.supabase.com:6543/postgres

# 교체 후 (실제 값)
postgresql://postgres.abc...:MyRealP%40ssw0rd@...pooler.supabase.com:6543/postgres
```

> **비밀번호에 특수문자가 있으면 URL 인코딩이 필요합니다.**
> 예: `@` → `%40`, `#` → `%23`, `&` → `%26`. [URL 인코더](https://www.urlencoder.org/)로 변환하세요.

---

## 3단계: `.env.local` 작성

### 3-1. 템플릿 복사

프로젝트 루트에서:

```bash
cp .env.example .env.local
```

### 3-2. 복사한 6개 값 붙여넣기

[.env.local](../.env.local)을 열어 2단계에서 복사한 값으로 교체합니다.

```bash
# ================================================================
# Supabase 공개 키
# ================================================================
NEXT_PUBLIC_SUPABASE_URL=https://abcdefgh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...

# 서버 전용 — 절대 클라이언트 코드에서 import 금지
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1...

# ================================================================
# Drizzle → Supabase Postgres
# ================================================================
# 앱 런타임용 (Transaction Pooler, 6543)
DATABASE_URL=postgresql://postgres.abcdefgh:비밀번호@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres

# 마이그레이션 전용 (Direct, 5432)
DIRECT_URL=postgresql://postgres.abcdefgh:비밀번호@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

### 3-3. 보안 체크리스트

- [ ] `.env.local`이 [.gitignore](../.gitignore)에 포함되어 있는가? (Next.js 기본 설정에 포함됨)
- [ ] `SUPABASE_SERVICE_ROLE_KEY`를 Client Component에서 `process.env.*`로 참조하지 않는가?
- [ ] 배포 시에는 Vercel 환경변수에 **같은 6개를 따로 등록**했는가?

---

## 4단계: 스키마 마이그레이션 (Drizzle)

이제 로컬 `src/db/schema.ts`를 실제 Supabase DB에 적용합니다.

### 4-1. 마이그레이션 파일 생성

```bash
pnpm db:generate
```

**동작**: [src/db/schema.ts](../src/db/schema.ts)를 읽어서 [src/db/migrations/](../src/db/migrations/)에 SQL 파일을 생성합니다. Git에 커밋해야 하는 파일입니다.

**확인**: `src/db/migrations/0000_xxx.sql` 같은 파일이 생겼는지 & 내용이 예상한 SQL인지 확인.

### 4-2. 마이그레이션 실행

```bash
pnpm db:migrate
```

**동작**: `DIRECT_URL`로 Supabase DB에 접속해서 마이그레이션 SQL을 순서대로 적용합니다. 이미 적용된 건 건너뜁니다.

**확인 방법**: Supabase Dashboard → **Table Editor**에서 `users`, `posts` 테이블이 생겼는지 확인.

> **⚠️ `db:push`는 쓰지 마세요.** `db:push`는 마이그레이션 파일 없이 스키마를 직접 푸시하는데, **히스토리가 남지 않아 배포 환경 동기화가 깨집니다**. 항상 `generate → migrate` 2단계로.

### 4-3. Supabase 초기 SQL 실행 (최초 1회)

RLS 안전망 활성화와 Auth 트리거 설치입니다. **회원가입이 작동하려면 반드시 실행**해야 합니다.

1. Supabase Dashboard → 좌측 **SQL Editor** 클릭
2. **+ New query**
3. [src/db/setup.sql](../src/db/setup.sql)의 내용을 **전체 복사해서 붙여넣기**
4. 우측 하단 **Run** 클릭 (또는 `Cmd+Enter`)
5. 하단 결과창에 `Success. No rows returned` 표시되면 완료

**확인**:
- Dashboard → Database → **Triggers**에 `on_auth_user_created` 있는지
- Table Editor → `users` 테이블 → **RLS enabled** 표시 있는지

---

## 5단계: 연결 확인

### 5-1. 개발 서버 실행

```bash
pnpm dev
```

[http://localhost:4739](http://localhost:4739) 접속 → 로그인 페이지 렌더링되면 **환경변수 OK**.

### 5-2. 회원가입 흐름 테스트

1. `/login`에서 Google 로그인 (또는 Email) 시도
2. 로그인 성공 후 Supabase Dashboard → **Authentication → Users**에 행 추가됐는지
3. **Table Editor → users**에 같은 user_id로 행이 자동 복제됐는지 ← **setup.sql의 트리거가 잘 동작하는지 검증**

### 5-3. Drizzle 연결 테스트

```bash
pnpm db:studio
```

브라우저에서 `https://local.drizzle.studio` 열리며 Supabase DB에 GUI로 접속됩니다. 테이블 브라우징 가능하면 `DATABASE_URL`도 정상.

---

## 스키마를 변경하고 싶을 때

1. [src/db/schema.ts](../src/db/schema.ts) 수정
2. `pnpm db:generate` → 새 마이그레이션 SQL 파일 생성
3. **생성된 SQL 내용을 반드시 검토** (특히 파괴적 변경: 컬럼 삭제, 타입 변경)
4. `pnpm db:migrate` → 로컬/개발 DB에 적용
5. 커밋 & 푸시 → 배포 시 `pnpm build` 안에서 자동 `drizzle-kit migrate` 실행

---

## 자주 겪는 문제

### `Tenant or user not found`
→ `DATABASE_URL` / `DIRECT_URL`의 **username 부분**(`postgres.xxxxx`)이 잘못됨. Dashboard → Database → Connection string에서 정확히 복사.

### `password authentication failed`
→ 비밀번호에 특수문자가 있는데 URL 인코딩 안 했거나, 비밀번호 자체가 틀림. 잊어버렸다면 Dashboard → Database → **Reset database password**.

### `SUPABASE_SERVICE_ROLE_KEY is not defined` (서버 로그)
→ `.env.local` 파일명/위치 오타. **프로젝트 루트**에 있어야 하며, 파일명은 정확히 `.env.local`.

### 환경변수 변경 후 반영 안 됨
→ Next.js는 `.env.local`을 **빌드 시에만 로드**합니다. dev 서버 재시작(`Ctrl+C` → `pnpm dev`) 필요.

### `Error: getaddrinfo ENOTFOUND db.xxxxx.supabase.co` (마이그레이션 시)
→ `DIRECT_URL`을 **Direct connection 탭**에서 복사한 경우 발생. 이 호스트는 IPv6 전용이라 일반 네트워크에서 DNS 조회 실패. **Session pooler 탭(포트 5432)의 URI로 교체**하세요 — 호스트 형식은 `aws-0-<region>.pooler.supabase.com`.

---

## 다음 단계

- 배포: [README.md#배포-vercel](../README.md) 참조
- AI 에이전트 작업 규칙: [CLAUDE.md](../CLAUDE.md)
- 설계 철학: [../../strategies/2026-04-20-Supabase-Nextjs-입문-가이드.md](../../strategies/2026-04-20-Supabase-Nextjs-입문-가이드.md)
