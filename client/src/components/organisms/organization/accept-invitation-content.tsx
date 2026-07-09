"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ApiError } from "@/lib/api/client";
import { acceptOrganizationInvitation } from "@/lib/api/organizations";
import { buildAuthRedirectPath } from "@/lib/auth/callback-url";
import { useAuth } from "@/lib/hooks/use-auth";
import { refreshAcceptedOrganizationInvitationQueries } from "@/lib/query/organization-invitations";

type Status = "loading" | "success" | "invalid_token" | "missing_token" | "error";

export function AcceptInvitationContent() {
  const t = useTranslations("invitations.accept");
  const searchParams = useSearchParams();
  const { token, isLoading: authLoading } = useAuth();
  const queryClient = useQueryClient();
  const invitationToken = searchParams.get("token");
  const callbackUrl = invitationToken ? `/invitations/accept?${searchParams.toString()}` : null;
  const [status, setStatus] = useState<Status>(invitationToken ? "loading" : "missing_token");
  const called = useRef(false);

  useEffect(() => {
    if (authLoading || called.current || !invitationToken) return;
    if (!token) return;

    called.current = true;
    acceptOrganizationInvitation(token, { token: invitationToken })
      .then(async () => {
        await refreshAcceptedOrganizationInvitationQueries(queryClient);
        setStatus("success");
      })
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 422) {
          setStatus("invalid_token");
        } else {
          setStatus("error");
        }
      });
  }, [authLoading, token, searchParams, invitationToken, queryClient]);

  if (!authLoading && invitationToken && !token) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">{t("unauthenticated")}</p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={buildAuthRedirectPath("/login", callbackUrl)}
            className="text-sm font-medium underline underline-offset-4"
          >
            {t("signIn")}
          </Link>
          <Link
            href={buildAuthRedirectPath("/register", callbackUrl)}
            className="text-sm font-medium underline underline-offset-4"
          >
            {t("createAccount")}
          </Link>
        </div>
      </div>
    );
  }

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
