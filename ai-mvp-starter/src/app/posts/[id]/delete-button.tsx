"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function DeleteButton({ postId }: { postId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleDelete() {
    if (!confirm("정말 삭제할까요?")) return;

    setLoading(true);
    try {
      await api.posts.remove(postId);
      router.push("/posts");
      router.refresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "삭제 실패");
      setLoading(false);
    }
  }

  return (
    <Button variant="outline" onClick={handleDelete} disabled={loading}>
      {loading ? "삭제 중..." : "삭제"}
    </Button>
  );
}
