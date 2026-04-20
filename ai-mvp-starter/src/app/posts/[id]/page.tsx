import { eq } from "drizzle-orm";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button";
import { db } from "@/db";
import { posts } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { DeleteButton } from "./delete-button";

type Props = { params: Promise<{ id: string }> };

export default async function PostDetailPage({ params }: Props) {
  const { id } = await params;

  const [user, post] = await Promise.all([
    getCurrentUser(),
    db.query.posts.findFirst({
      where: eq(posts.id, id),
      with: { author: true },
    }),
  ]);

  if (!post) notFound();

  const isOwner = user?.id === post.authorId;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <Link href="/posts" className="text-sm text-gray-500 hover:underline">
        ← 목록으로
      </Link>

      <article className="mt-4">
        <h1 className="text-3xl font-semibold">{post.title}</h1>
        <p className="mt-2 text-sm text-gray-500">
          {post.author?.name ?? "익명"} · {new Date(post.createdAt).toLocaleDateString("ko-KR")}
        </p>

        <div className="mt-6 whitespace-pre-wrap text-gray-800">{post.content}</div>

        {isOwner && (
          <div className="mt-8 flex gap-2">
            <Link href={`/posts/${post.id}/edit`}>
              <Button variant="outline">수정</Button>
            </Link>
            <DeleteButton postId={post.id} />
          </div>
        )}
      </article>
    </main>
  );
}
