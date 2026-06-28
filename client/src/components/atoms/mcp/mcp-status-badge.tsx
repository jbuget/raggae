import { useTranslations } from "next-intl";

type McpStatusBadgeProps = {
  isActive: boolean;
};

export function McpStatusBadge({ isActive }: McpStatusBadgeProps) {
  const tCommon = useTranslations("common");
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        isActive
          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
          : "bg-muted text-muted-foreground"
      }`}
    >
      {isActive ? tCommon("active") : tCommon("inactive")}
    </span>
  );
}
