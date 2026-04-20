import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <h2 className="text-xl font-semibold">페이지를 찾을 수 없어요</h2>
      <Link href="/">
        <Button>홈으로</Button>
      </Link>
    </div>
  );
}
