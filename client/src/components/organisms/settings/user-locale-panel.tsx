"use client";

import { useLocale, useTranslations } from "next-intl";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
        <Select
          defaultValue={currentLocale}
          onValueChange={(val) => {
            const locale = val as UpdateUserLocaleRequest["locale"];
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
        >
          <SelectTrigger id="locale-select" className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {LOCALE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                <span className="flex items-center gap-2">
                  <span>{opt.flag}</span>
                  <span>{opt.label}</span>
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </Card>
  );
}
