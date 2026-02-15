"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/projects");
    }
  }, [status, router]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8">
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold">Raggae</h1>
        <p className="text-xl text-muted-foreground max-w-md">
          RAG Generator Agent Expert — Create conversational agents powered by
          your documents.
        </p>
      </div>
      <div className="flex gap-4">
        <Button asChild size="lg">
          <Link href="/login">Sign In</Link>
        </Button>
        <Button asChild variant="outline" size="lg">
          <Link href="/register">Register</Link>
        </Button>
      </div>
    </div>
  );
}
