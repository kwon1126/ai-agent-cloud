import Link from "next/link";
import { Button } from "@/components/ui/button";
import { getCurrentUser } from "@/lib/auth";

export default async function HomePage() {
  const user = await getCurrentUser();

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center px-4 text-center">
      <h1 className="text-4xl font-semibold tracking-tight">AI MVP Starter</h1>
      <p className="mt-4 text-gray-500">
        Next.js + Supabase + Drizzle 풀스택 템플릿
      </p>

      {!user && (
        <div className="mt-8">
          <Link href="/login">
            <Button>로그인</Button>
          </Link>
        </div>
      )}
    </main>
  );
}
