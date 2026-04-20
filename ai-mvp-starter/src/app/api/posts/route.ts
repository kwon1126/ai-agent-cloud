import { desc } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { type NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { posts } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";

export async function GET() {
  const result = await db.query.posts.findMany({
    with: { author: true },
    orderBy: [desc(posts.createdAt)],
    limit: 50,
  });
  return NextResponse.json(result);
}

export async function POST(req: NextRequest) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await req.json().catch(() => null);
  if (!body?.title) {
    return NextResponse.json({ error: "title is required" }, { status: 400 });
  }

  const [created] = await db
    .insert(posts)
    .values({
      title: body.title,
      content: body.content ?? null,
      published: body.published ?? false,
      authorId: user.id,
    })
    .returning();

  revalidatePath("/posts");
  return NextResponse.json(created, { status: 201 });
}
