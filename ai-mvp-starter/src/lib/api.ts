import type { NewPost, Post } from "@/db/schema";

/**
 * Client Component에서 Route Handler를 호출하는 fetch 헬퍼.
 * Server Component에서는 사용 금지 — DB를 직접 호출하세요.
 */
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

type PostWithAuthor = Post & { author: { id: string; email: string; name: string | null } };

export const api = {
  posts: {
    list: () => request<PostWithAuthor[]>("/api/posts"),
    get: (id: string) => request<PostWithAuthor>(`/api/posts/${id}`),
    create: (data: Pick<NewPost, "title" | "content" | "published">) =>
      request<Post>("/api/posts", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Partial<Pick<NewPost, "title" | "content" | "published">>) =>
      request<Post>(`/api/posts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    remove: (id: string) => request<{ ok: true }>(`/api/posts/${id}`, { method: "DELETE" }),
  },
};
