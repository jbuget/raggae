import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  const entraEnabled = process.env.ENTRA_ENABLED === "true";
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

  return (
    <Suspense>
      <LoginForm entraEnabled={entraEnabled} backendUrl={backendUrl} />
    </Suspense>
  );
}
