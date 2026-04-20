import { and, eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { type NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { posts } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;

  const post = await db.query.posts.findFirst({
    where: eq(posts.id, id),
    with: { author: true },
  });

  if (!post) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(post);
}

export async function PATCH(req: NextRequest, { params }: Params) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  const body = await req.json().catch(() => ({}));

  // 인가: 작성자 본인만 수정 가능 (RLS 아닌 서버에서 직접 체크)
  const existing = await db.query.posts.findFirst({ where: eq(posts.id, id) });
  if (!existing) return NextResponse.json({ error: "Not found" }, { status: 404 });
  if (existing.authorId !== user.id) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const [updated] = await db
    .update(posts)
    .set({
      title: body.title ?? existing.title,
      content: body.content ?? existing.content,
      published: body.published ?? existing.published,
      updatedAt: new Date(),
    })
    .where(eq(posts.id, id))
    .returning();

  revalidatePath("/posts");
  revalidatePath(`/posts/${id}`);
  return NextResponse.json(updated);
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;

  const [deleted] = await db
    .delete(posts)
    .where(and(eq(posts.id, id), eq(posts.authorId, user.id)))
    .returning();

  if (!deleted) {
    return NextResponse.json({ error: "Not found or forbidden" }, { status: 404 });
  }

  revalidatePath("/posts");
  return NextResponse.json({ ok: true });
}
