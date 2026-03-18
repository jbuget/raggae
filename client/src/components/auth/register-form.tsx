"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "next-intl";
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
import { register } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

export function RegisterForm() {
  const t = useTranslations("auth.register");
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const isDisabled = !email || !password || !fullName || password.length < 8 || isLoading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError(t("passwordMinLength"));
      return;
    }

    setIsLoading(true);

    try {
      await register({ email, password, full_name: fullName });
      router.push("/login");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError(t("emailAlreadyExists"));
      } else {
        setError(t("unexpectedError"));
      }
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
            <Label htmlFor="fullName">{t("fullNameLabel")}</Label>
            <Input
              id="fullName"
              type="text"
              placeholder={t("fullNamePlaceholder")}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
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
            {password.length > 0 && password.length < 8 && (
              <p className="text-sm text-muted-foreground">
                {t("passwordMinLength")}
              </p>
            )}
          </div>
          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          <Button type="submit" className="w-full" disabled={isDisabled}>
            {isLoading ? t("creatingAccount") : t("createAccount")}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            {t("alreadyHaveAccount")}{" "}
            <a href="/login" className="text-primary hover:underline">
              {t("signIn")}
            </a>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
