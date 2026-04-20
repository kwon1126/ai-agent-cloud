# AI MVP Starter

> Next.js 16 + Supabase + Drizzle 기반의 AI 에이전트 친화 MVP 스타터 템플릿

## 철학

- **DB의 RLS/함수에 비즈니스 로직을 넣지 않는다** — 모든 인가/검증은 Route Handler에서 TypeScript로
- **Route Handler 100%** — Server Action은 폼 제출에만 제한적으로
- **Server Component 우선** — 상호작용이 필요할 때만 `'use client'`
- **테스트 = AI 루프의 종료 조건** — Given-When-Then 스펙 → 테스트 → 구현 순

자세한 규칙은 [CLAUDE.md](./CLAUDE.md) 참조.

## 10분 세팅 가이드

> **처음 사용하신다면 [Supabase 연결 상세 가이드](./docs/supabase-setup.md)를 따라 진행하세요** — 스크린샷 없이 글만으로 따라할 수 있도록 단계별로 정리되어 있습니다.

### 1. Supabase 프로젝트 생성
[supabase.com](https://supabase.com) → New Project 생성 후:
- Project Settings → API: `Project URL`, `anon public` 키, `service_role` 키 복사
- Project Settings → Database: **Connection string** 두 종류 복사
  - **Transaction Pooler (6543)** → `DATABASE_URL`
  - **Direct connection (5432)** → `DIRECT_URL`

### 2. 환경변수 설정
```bash
cp .env.example .env.local
# .env.local 편집 — 위에서 복사한 값 입력
```

### 3. 의존성 설치
```bash
# pnpm 미설치 시 먼저 설치 (Node 16.13+ 권장)
corepack enable
corepack prepare pnpm@latest --activate

# 의존성 설치
pnpm install
```

> **왜 pnpm?** 디스크 효율(심볼릭 링크로 중복 제거), 설치 속도, 모노레포 확장성. Next.js 공식 권장.

### 4. 스키마 마이그레이션
```bash
# schema.ts에서 SQL 마이그레이션 파일 생성
pnpm db:generate

# Supabase DB에 적용
pnpm db:migrate
```

### 5. Supabase 초기 설정 SQL 실행
Supabase Dashboard → SQL Editor에서 [src/db/setup.sql](./src/db/setup.sql) 내용 실행:
- RLS "안전망" 활성화 (정책 없음 = deny)
- `auth.users` → `public.users` 자동 동기화 트리거

### 6. 개발 서버 실행
```bash
pnpm dev
# http://localhost:4739
```

### 7. Google OAuth 활성화 (선택)
Supabase Dashboard → Authentication → Providers → Google:
- Google Cloud Console에서 OAuth Client 생성
- Redirect URL: `https://<프로젝트ref>.supabase.co/auth/v1/callback`
- 클라이언트 ID/Secret을 Supabase에 입력

## 디렉토리 구조

```
src/
  app/
    api/posts/                 Route Handlers (CRUD)
    auth/callback/             OAuth 콜백
    auth/signout/              로그아웃
    login/                     로그인 페이지
    posts/                     게시글 목록/상세/작성
  components/ui/               Button, Input (shadcn 스타일)
  db/
    schema.ts                  Drizzle 스키마 (단일 파일)
    index.ts                   DB 클라이언트
    migrations/                drizzle-kit 자동 관리
    setup.sql                  Supabase 초기 SQL
  lib/
    supabase/client.ts         Browser Client
    supabase/server.ts         Server Client
    supabase/middleware.ts     Middleware Client
    auth.ts                    getCurrentUser, requireUser
    api.ts                     Client→Route Handler fetch 헬퍼
tests/                         Vitest + Supertest 통합 테스트
middleware.ts                  세션 자동 갱신
```

## 스크립트

| 명령 | 용도 |
|---|---|
| `pnpm dev` | 개발 서버 (Turbopack, port 4739) |
| `pnpm build` | 마이그레이션 + 프로덕션 빌드 |
| `pnpm test` | Vitest 테스트 실행 |
| `pnpm lint` | Biome 포맷/린트 체크 (CI용) |
| `pnpm lint:fix` | Biome 자동 수정 |
| `pnpm format` | Biome 포맷 전용 자동 적용 |
| `pnpm typecheck` | `tsc --noEmit` 타입 체크 |
| `pnpm db:generate` | 스키마 변경 → SQL 마이그레이션 생성 |
| `pnpm db:migrate` | 마이그레이션 DB에 적용 |
| `pnpm db:studio` | Drizzle Studio (GUI) |

## 배포 (Vercel)

1. GitHub에 푸시
2. Vercel → Import Git Repository
3. 환경변수 6개 모두 Vercel에 등록:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `DATABASE_URL`
   - `DIRECT_URL`
4. Install Command를 `pnpm install`로, Build Command를 `pnpm build`로 설정 (Vercel이 자동 감지하는 경우 생략 가능)
5. Deploy

`pnpm build`가 자동으로 `drizzle-kit migrate` → `next build` 순으로 실행됩니다.

## 참고 문서

- [전략 문서: Supabase + Next.js 입문 아키텍처](../../strategies/2026-04-20-Supabase-Nextjs-입문-가이드.md)
- [전략 문서: AI MVP 공장 기술 스택](../../strategies/2026-04-18-AI-MVP-공장-기술스택.md)
- [CLAUDE.md — AI 작업 규칙](./CLAUDE.md)
