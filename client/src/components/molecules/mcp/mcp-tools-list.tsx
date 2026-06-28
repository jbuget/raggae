import { useTranslations } from "next-intl";
import type { McpToolSnapshotResponse } from "@/lib/types/api";

type McpToolsListProps = {
  tools: McpToolSnapshotResponse[];
};

export function McpToolsList({ tools }: McpToolsListProps) {
  const t = useTranslations("organizations.mcpServers");

  if (tools.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("noTools")}</p>;
  }

  return (
    <ul className="space-y-1.5">
      {tools.map((tool) => (
        <li key={tool.name} className="rounded bg-muted/40 px-2 py-1.5 text-xs">
          <p className="font-mono font-medium">{tool.name}</p>
          {tool.description && (
            <p className="mt-0.5 text-muted-foreground">{tool.description}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
