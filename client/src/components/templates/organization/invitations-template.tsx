"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { UserInvitationsList } from "@/components/organisms/organization/user-invitations-list";

export function InvitationsTemplate() {
  const t = useTranslations("invitations.page");
  return (
    <PageTemplate title={t("title")} description={t("description")}>
      <UserInvitationsList />
    </PageTemplate>
  );
}
