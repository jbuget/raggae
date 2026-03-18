"use client";

import { useLocale, useTranslations } from "next-intl";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useUpdateUserLocale } from "@/lib/hooks/use-user-profile";
import { useAuth } from "@/lib/hooks/use-auth";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";

const LOCALE_FLAGS: Record<UpdateUserLocaleRequest["locale"], { flag: string; short: string }> = {
  en: { flag: "🇬🇧", short: "EN" },
  fr: { flag: "🇫🇷", short: "FR" },
};

const LOCALE_VALUES: Array<UpdateUserLocaleRequest["locale"]> = ["en", "fr"];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365; // 1 year
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function LocaleSelector() {
  const currentLocale = useLocale();
  const t = useTranslations("layout.localeSelector");
  const { isAuthenticated } = useAuth();
  const updateLocale = useUpdateUserLocale();

  const current = LOCALE_FLAGS[currentLocale as UpdateUserLocaleRequest["locale"]] ?? LOCALE_FLAGS.en;

  function handleSelect(locale: UpdateUserLocaleRequest["locale"]) {
    if (locale === currentLocale) return;

    setLocaleCookie(locale);

    if (isAuthenticated) {
      updateLocale.mutate(
        { locale },
        { onSettled: () => window.location.reload() },
      );
    } else {
      window.location.reload();
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-1">
          <span>{current.flag}</span>
          <span className="hidden sm:inline">{current.short}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {LOCALE_VALUES.map((value) => (
          <DropdownMenuItem
            key={value}
            onClick={() => handleSelect(value)}
            className={currentLocale === value ? "font-semibold" : ""}
          >
            {LOCALE_FLAGS[value].flag} {t(value)}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
