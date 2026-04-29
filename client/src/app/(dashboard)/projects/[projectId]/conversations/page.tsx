"use client";

import { useParams } from "next/navigation";
import { ConversationsTemplate } from "@/components/templates/project/conversations-template";

export default function ConversationsPage() {
  const params = useParams<{ projectId: string }>();
  return <ConversationsTemplate projectId={params.projectId} />;
}
