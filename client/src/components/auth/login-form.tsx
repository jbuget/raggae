"use client";

import { signIn, getSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { getCurrentUser } from "@/lib/api/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function LoginForm() {
  const t = useTranslations("auth.login");
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const isDisabled = !email || !password || isLoading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        setError(t("invalidCredentials"));
      } else {
        const session = await getSession();
        if (session?.accessToken) {
          const user = await getCurrentUser(session.accessToken);
          if (user.locale) {
            const maxAge = 60 * 60 * 24 * 365;
            document.cookie = `raggae_locale=${user.locale};path=/;max-age=${maxAge};SameSite=Lax`;
          }
        }
        router.push("/projects");
      }
    } catch {
      setError(t("unexpectedError"));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("title")}</CardTitle>
        <CardDescription>
          {t("subtitle")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">{t("emailLabel")}</Label>
            <Input
              id="email"
              type="email"
              placeholder={t("emailPlaceholder")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">{t("passwordLabel")}</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          <Button type="submit" className="w-full" disabled={isDisabled}>
            {isLoading ? t("signingIn") : t("signIn")}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            {t("noAccount")}{" "}
            <a href="/register" className="text-primary hover:underline">
              {t("register")}
            </a>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
