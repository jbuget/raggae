import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  const entraEnabled = process.env.NEXT_PUBLIC_ENTRA_ENABLED === "true";

  return (
    <Suspense>
      <LoginForm entraEnabled={entraEnabled} />
    </Suspense>
  );
}
