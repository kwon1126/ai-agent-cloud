/**
 * Posts Route Handler 통합 테스트 예제 (Supertest 스타일)
 *
 * AI 구현 루프의 종료 조건 — 이 테스트가 통과해야 PR이 가능.
 * 스펙(Given-When-Then) 먼저, 구현은 그 다음. 역순 금지.
 *
 * NOTE: Next.js Route Handler는 직접 import해 호출할 수 있음.
 *       실제 HTTP 테스트가 필요하면 `next dev` 띄우고 supertest(host) 패턴으로 확장.
 */

import { NextRequest } from "next/server";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { GET, POST } from "@/app/api/posts/route";

// 테스트 전 세팅: 테스트용 DB 정리 (실제로는 별도 테스트 DB 권장)
beforeAll(async () => {
  // TODO: 테스트 DB 준비 로직
});

afterAll(async () => {
  // TODO: 정리
});

describe("GET /api/posts", () => {
  it("Given 게시글이 없을 때 When 목록을 조회하면 Then 빈 배열을 반환한다", async () => {
    const res = await GET();
    expect(res.status).toBe(200);

    const json = await res.json();
    expect(Array.isArray(json)).toBe(true);
  });
});

describe("POST /api/posts", () => {
  it("Given 로그인하지 않았을 때 When 글을 작성하면 Then 401을 반환한다", async () => {
    const req = new NextRequest("http://localhost:3000/api/posts", {
      method: "POST",
      body: JSON.stringify({ title: "test" }),
    });
    const res = await POST(req);
    expect(res.status).toBe(401);
  });

  it.todo("Given 로그인 상태일 때 When 제목 없이 작성하면 Then 400을 반환한다");
  it.todo("Given 로그인 상태일 때 When 정상 입력하면 Then 201과 생성된 글을 반환한다");
});
