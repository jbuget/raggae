"use client";

import { useTranslations } from "next-intl";
import { UserInvitationsList } from "@/components/organisms/organization/user-invitations-list";

export default function InvitationsPage() {
  const t = useTranslations("invitations.page");
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>
      <p className="text-sm text-muted-foreground">
        {t("description")}
      </p>
      <UserInvitationsList />
    </div>
  );
}
