"use client";

import { useLocale, useTranslations } from "next-intl";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useUpdateUserLocale } from "@/lib/hooks/use-user-profile";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";

const LOCALE_OPTIONS: Array<{ value: UpdateUserLocaleRequest["locale"]; flag: string; label: string }> = [
  { value: "en", flag: "🇬🇧", label: "English" },
  { value: "fr", flag: "🇫🇷", label: "Français" },
];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365;
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function UserLocalePanel() {
  const t = useTranslations("settings");
  const currentLocale = useLocale();
  const updateUserLocale = useUpdateUserLocale();

  return (
    <Card className="space-y-4 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("language.title")}</h2>
        <p className="text-sm text-muted-foreground">{t("language.description")}</p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="locale-select">{t("language.label")}</Label>
        <select
          id="locale-select"
          defaultValue={currentLocale}
          onChange={(e) => {
            const locale = e.target.value as UpdateUserLocaleRequest["locale"];
            setLocaleCookie(locale);
            updateUserLocale.mutate(
              { locale },
              {
                onSuccess: () => {
                  toast.success(t("language.saveSuccess"));
                  window.location.reload();
                },
                onError: () => toast.error(t("language.saveError")),
              },
            );
          }}
          className="flex h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
        >
          {LOCALE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.flag} {opt.label}
            </option>
          ))}
        </select>
      </div>
    </Card>
  );
}
