import { useTranslations } from "next-intl";
import { BACKEND_LABELS } from "@/lib/constants/backends";

type FieldHintProps = {
  projectValue: string | number | boolean | null | undefined;
  inheritedValue: string | number | boolean | null | undefined;
  ownerType: "org" | "user" | "system";
  dirty?: boolean;
};

function formatValue(v: string | number | boolean): string {
  if (typeof v === "string") return BACKEND_LABELS[v] ?? v;
  return String(v);
}

export function FieldHint({ projectValue, inheritedValue, ownerType, dirty }: FieldHintProps) {
  const t = useTranslations("projects.settings.fieldHint");

  if (dirty) {
    return (
      <p className="text-xs flex items-center gap-1.5 pl-1 text-muted-foreground">
        <span className="h-1.5 w-1.5 rounded-full bg-blue-500 shrink-0" />
        {t("modified")}
      </p>
    );
  }

  if (inheritedValue == null) return null;

  const isCustomized = projectValue != null && projectValue !== inheritedValue;

  if (isCustomized) {
    const customizedLabel =
      ownerType === "org" ? t("customizedOrg") :
      ownerType === "user" ? t("customizedUser") :
      t("customizedSystem");
    return (
      <p className="text-xs flex items-center gap-1.5 pl-1 text-muted-foreground">
        <span className="h-1.5 w-1.5 rounded-full bg-white shrink-0" />
        <span>
          {customizedLabel}
          {" "}
          <span className="font-medium">{formatValue(inheritedValue)}</span>
        </span>
      </p>
    );
  }

  const inheritedLabel =
    ownerType === "org" ? t("inheritedFromOrg") :
    ownerType === "user" ? t("inheritedFromUser") :
    t("inheritedFromSystem");

  return (
    <p className="text-xs flex items-center gap-1.5 text-muted-foreground">
      <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/40 shrink-0" />
      {inheritedLabel}
    </p>
  );
}
