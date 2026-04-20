# AI 에이전트 작업 규칙 (AI MVP Starter)

이 문서는 AI 코딩 에이전트(Claude Code 등)가 이 템플릿에서 일관되게 작업하기 위한 **실질적 헌법**이다. 이 5가지 규칙을 어기면 전체 아키텍처가 무너진다.

## 스택 고정

- Next.js 16 App Router + TypeScript
- Drizzle ORM + Supabase Postgres
- Supabase Auth (@supabase/ssr)
- Tailwind CSS v4 + 최소 shadcn 스타일 컴포넌트
- Vitest + Supertest

**스택 변경 금지.** 사용자가 명시적으로 요청하지 않는 한 라이브러리 추가/교체 제안하지 말 것.

---

## 규칙 1: API 레이어는 Route Handlers 기본

```
✅ app/api/**/route.ts          ← 모든 API
❌ Server Action                ← 폼 제출 + 단순 UI 상태 변경에만 허용
```

**왜**: Express+Supertest 훈련 데이터 재활용, 테스트 가능성, Server/Client 경계 명확화.

**적용**:
- 비즈니스 로직(결제, 외부 API, DB 트랜잭션, 복잡한 유효성 검증)은 **반드시 Route Handler**
- 모든 Route Handler는 `tests/` 폴더에 Supertest 스타일 테스트 작성
- Server Action을 제안하기 전 "이게 정말 단순 폼 제출인가?" 자문

---

## 규칙 2: 인가는 Route Handler에서 직접 체크 (RLS 금지)

```typescript
// ✅ 올바른 패턴
const user = await getCurrentUser();
if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

const existing = await db.query.posts.findFirst({ where: eq(posts.id, id) });
if (existing.authorId !== user.id) {
  return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
}
```

**왜**: 비즈니스 로직은 TypeScript에. RLS 정책 + DB 함수 + `auth.uid()` 경로는 의도적으로 **배제**. 디버깅 복잡도와 이전 비용을 선제 차단.

**절대 금지**:
- `create policy` SQL 작성 (안전망용 `enable row level security`는 예외)
- `auth.uid()` 의존한 쿼리 설계
- DB 함수/트리거에 비즈니스 로직 심기 (setup.sql의 `handle_new_user` 같은 동기화 트리거는 예외)

---

## 규칙 3: 데이터 페칭 — Server Component 우선

```
✅ Server Component (async 함수)에서 db.query.xxx 직접 호출  ← 80% 케이스
✅ Client Component에서 fetch('/api/...')                   ← 상호작용 시
❌ Server Component에서 fetch('/api/...')                   ← 자기 자신 호출 금지
❌ 'use client' 남발                                         ← 상호작용 없으면 Server
```

**왜**: 네트워크 홉 제거, 타입 자동 추론, SEO/성능 유리.

**'use client'가 필요한 경우만**:
- `useState`, `useEffect` 등 훅
- `onClick`, `onChange` 이벤트 핸들러
- 브라우저 API (`localStorage`, `window`)

그 외에는 Server Component. 특히 목록/상세 페이지는 항상 Server.

---

## 규칙 4: 변경 작업 후 캐시 무효화 필수

```typescript
// Route Handler에서
import { revalidatePath } from 'next/cache';

await db.insert(posts).values(...);
revalidatePath('/posts');           // 필수
return NextResponse.json(created, { status: 201 });
```

```typescript
// Client Component에서 추가로
router.refresh();   // 현재 라우트의 Server Component 재실행
```

**왜**: Server Component의 DB 쿼리는 기본 캐시됨. 변경 후 갱신 안 하면 "수정했는데 목록에 안 보여요" 발생.

**체크리스트**: POST/PATCH/DELETE Route Handler의 응답 직전에 `revalidatePath` 호출했는지 확인.

---

## 규칙 5: 테스트는 스펙에서 먼저 도출

```
스펙(Given-When-Then) → 테스트 작성 → AI 구현 → 테스트 통과 → 완료
```

**절대 금지**: AI가 구현을 먼저 하고 그에 맞춰 테스트 작성. 테스트가 의미 없어짐.

**작성 규칙**:
- 모든 Route Handler는 통합 테스트 필수
- 테스트 파일명: `tests/<domain>.test.ts`
- `describe("HTTP_METHOD /path", ...)` 형식
- 각 `it`는 Given-When-Then 한 문장으로 제목 작성
- 실패 메시지가 구체적이어야 함 (AI 루프의 감각 기관)

**테스트 우회/형식적 작성 감지 시**: PR 거부.

---

## 파일 배치 규칙 (AI가 헷갈리는 지점)

```
src/
  app/
    (routes)/page.tsx          ← Server Component (async 함수)
    (routes)/xxx-form.tsx      ← Client Component ('use client')
    api/**/route.ts            ← Route Handler
  lib/
    supabase/client.ts         ← Client Component 전용
    supabase/server.ts         ← Server Component / Route Handler 전용
    supabase/middleware.ts     ← middleware.ts 전용
    auth.ts                    ← getCurrentUser, requireUser
    api.ts                     ← Client→Route Handler fetch 헬퍼
    utils.ts                   ← cn(), 순수 유틸
  db/
    index.ts                   ← Drizzle 클라이언트
    schema.ts                  ← 단일 스키마 파일
    migrations/                ← drizzle-kit이 관리, 직접 편집 금지
    setup.sql                  ← Supabase 초기 설정 (RLS enable, 트리거)
  components/ui/               ← 재사용 UI 컴포넌트 (Button, Input...)
tests/                         ← Supertest 스타일 통합 테스트
```

---

## 환경변수 보안

| 변수 | 노출 여부 |
|---|---|
| `NEXT_PUBLIC_*` | 브라우저 OK |
| `SUPABASE_SERVICE_ROLE_KEY` | **서버 전용** — 클라이언트 번들 유입 치명적 |
| `DATABASE_URL`, `DIRECT_URL` | 서버 전용 |

**Client Component에서 `process.env.SUPABASE_SERVICE_ROLE_KEY` 사용 금지.** 이 키는 MySQL root 비밀번호급.

---

## 작업 흐름 체크리스트

구현 시작 전:
- [ ] 스펙이 Given-When-Then 형식인가? 모호하면 플랜 단계에서 반려.
- [ ] 테스트를 먼저 작성했는가?
- [ ] 스키마 변경이 필요하면 `db:generate` → SQL 확인 → `db:migrate`.

구현 중:
- [ ] Server Component에서 fetch로 자기 API 안 부르는가?
- [ ] Route Handler에 `getCurrentUser()` 인가 체크 있는가?
- [ ] 변경 작업에 `revalidatePath` 호출 있는가?
- [ ] 'use client'가 정말 필요한가?

구현 후:
- [ ] 모든 Route Handler에 통합 테스트 있는가?
- [ ] 테스트가 전부 통과하는가?
- [ ] Service Role Key가 클라이언트 번들에 유입되지 않는가?
