"use client";

import { Suspense } from "react";
import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { AcceptInvitationContent } from "@/components/organisms/organization/accept-invitation-content";

export function AcceptInvitationTemplate() {
  const t = useTranslations("invitations.page");
  return (
    <PageTemplate title={t("title")}>
      <Suspense>
        <AcceptInvitationContent />
      </Suspense>
    </PageTemplate>
  );
}
