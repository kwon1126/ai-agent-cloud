import { desc } from "drizzle-orm";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { db } from "@/db";
import { posts } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";

export default async function PostsPage() {
  const [user, list] = await Promise.all([
    getCurrentUser(),
    db.query.posts.findMany({
      with: { author: true },
      orderBy: [desc(posts.createdAt)],
      limit: 50,
    }),
  ]);

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">게시글</h1>
        {user ? (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">{user.email}</span>
            <Link href="/posts/new">
              <Button>새 글 작성</Button>
            </Link>
            <form action="/auth/signout" method="post">
              <Button type="submit" variant="outline">
                로그아웃
              </Button>
            </form>
          </div>
        ) : (
          <Link href="/login">
            <Button variant="outline">로그인</Button>
          </Link>
        )}
      </header>

      {list.length === 0 ? (
        <p className="text-gray-500">아직 작성된 글이 없어요.</p>
      ) : (
        <ul className="divide-y">
          {list.map((post) => (
            <li key={post.id} className="py-4">
              <Link
                href={`/posts/${post.id}`}
                className="block hover:bg-gray-50"
              >
                <h2 className="font-medium">{post.title}</h2>
                <p className="mt-1 text-sm text-gray-500">
                  {post.author?.name ?? "익명"} ·{" "}
                  {new Date(post.createdAt).toLocaleDateString("ko-KR")}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
