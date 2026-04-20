import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

/**
 * 현재 로그인한 사용자를 반환. 없으면 null.
 * 서버에서 반드시 getUser() 사용 — getSession()은 쿠키를 검증 없이 신뢰하므로 위조 가능.
 */
export async function getCurrentUser() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

/**
 * 로그인 필수 페이지에서 사용. 미로그인 시 /login으로 리다이렉트.
 */
export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  return user;
}
