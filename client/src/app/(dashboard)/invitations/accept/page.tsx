"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { acceptOrganizationInvitation } from "@/lib/api/organizations";
import { useAuth } from "@/lib/hooks/use-auth";

type Status = "loading" | "success" | "invalid_token" | "missing_token" | "error";

function AcceptInvitationContent() {
  const t = useTranslations("invitations.accept");
  const searchParams = useSearchParams();
  const { token, isLoading: authLoading } = useAuth();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<Status>("loading");
  const called = useRef(false);

  useEffect(() => {
    if (authLoading || called.current) return;

    const invitationToken = searchParams.get("token");
    if (!invitationToken) {
      setStatus("missing_token");
      return;
    }

    if (!token) return;

    called.current = true;
    acceptOrganizationInvitation(token, { token: invitationToken })
      .then(() => {
        queryClient.invalidateQueries({ queryKey: ["organizations"] });
        setStatus("success");
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "";
        if (message.includes("422") || message.includes("invalid") || message.includes("expired")) {
          setStatus("invalid_token");
        } else {
          setStatus("error");
        }
      });
  }, [authLoading, token, searchParams]);

  if (status === "loading") {
    return <p className="text-sm text-muted-foreground">{t("loading")}</p>;
  }

  if (status === "success") {
    return (
      <div className="space-y-4">
        <p className="text-sm text-green-600">{t("success")}</p>
        <Link href="/organizations" className="text-sm font-medium underline underline-offset-4">
          {t("goToOrganizations")}
        </Link>
      </div>
    );
  }

  const message =
    status === "missing_token"
      ? t("missingToken")
      : status === "invalid_token"
        ? t("invalidToken")
        : t("error");

  return <p className="text-sm text-destructive">{message}</p>;
}

export default function AcceptInvitationPage() {
  const t = useTranslations("invitations.page");
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>
      <AcceptInvitationContent />
    </div>
  );
}
