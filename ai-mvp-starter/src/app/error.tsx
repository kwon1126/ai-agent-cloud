"use client";

import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <h2 className="text-xl font-semibold">문제가 발생했어요</h2>
      <p className="text-sm text-gray-500">{error.message}</p>
      <Button onClick={reset}>다시 시도</Button>
    </div>
  );
}
