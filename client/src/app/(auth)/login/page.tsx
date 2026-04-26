import { Suspense } from "react";
import { LoginForm } from "@/components/molecules/auth/login-form";

export default function LoginPage() {
  const entraEnabled = process.env.ENTRA_ENABLED === "true";
  const backendUrl = process.env.PUBLIC_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

  return (
    <Suspense>
      <LoginForm entraEnabled={entraEnabled} backendUrl={backendUrl} />
    </Suspense>
  );
}
