"use client";

import { useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { signIn } from "next-auth/react";
import { Suspense } from "react";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

function EntraCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    const code = searchParams.get("code");
    const redirect = searchParams.get("redirect") || "/projects";

    if (!code) {
      router.replace("/login");
      return;
    }

    async function exchange() {
      try {
        const tokenResp = await fetch(`${BACKEND_URL}/api/v1/auth/entra/token`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        });

        if (!tokenResp.ok) {
          router.replace("/login?error=sso");
          return;
        }

        const { access_token } = await tokenResp.json();

        const result = await signIn("entra-token", {
          accessToken: access_token,
          redirect: false,
        });

        if (result?.error) {
          router.replace("/login?error=sso");
        } else {
          router.replace(redirect);
        }
      } catch {
        router.replace("/login?error=sso");
      }
    }

    exchange();
  }, [searchParams, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-muted-foreground text-sm">Connexion en cours...</p>
    </div>
  );
}

export default function EntraCallbackPage() {
  return (
    <Suspense>
      <EntraCallback />
    </Suspense>
  );
}
