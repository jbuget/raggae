"use client";

import Link from "next/link";
import { MessageSquarePlus } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTemplate } from "@/components/templates/page-template";
import { ConversationList } from "@/components/organisms/project/conversation-list";
import { ProjectName } from "@/components/organisms/project/project-name";

type ConversationsTemplateProps = {
  projectId: string;
};

export function ConversationsTemplate({ projectId }: ConversationsTemplateProps) {
  const t = useTranslations("conversations");

  return (
    <PageTemplate
      title={<ProjectName projectId={projectId} />}
      description={t("title")}
      actions={
        <Button asChild>
          <Link href={`/projects/${projectId}/chat`}>
            <MessageSquarePlus className="mr-2 h-4 w-4" />
            {t("new")}
          </Link>
        </Button>
      }
    >
      <ConversationList projectId={projectId} />
    </PageTemplate>
  );
}
