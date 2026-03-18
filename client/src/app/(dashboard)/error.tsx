"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const t = useTranslations("errors.error");
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <h1 className="text-2xl font-bold">{t("title")}</h1>
      <p className="text-muted-foreground">
        {error.message || t("message")}
      </p>
      <Button onClick={reset}>{t("retry")}</Button>
    </div>
  );
}
