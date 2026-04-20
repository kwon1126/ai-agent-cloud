import { requireUser } from "@/lib/auth";
import { PostForm } from "./post-form";

export default async function NewPostPage() {
  await requireUser();

  return (
    <main className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-semibold">새 글 작성</h1>
      <PostForm />
    </main>
  );
}
