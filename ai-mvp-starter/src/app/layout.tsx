import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI MVP Starter",
  description: "Next.js + Supabase + Drizzle MVP starter",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-white text-gray-900 antialiased">{children}</body>
    </html>
  );
}
