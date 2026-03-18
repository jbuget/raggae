"use client";

import { useLocale } from "next-intl";
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

const LOCALES: Array<{ value: UpdateUserLocaleRequest["locale"]; flag: string; label: string; short: string }> = [
  { value: "en", flag: "🇬🇧", label: "English", short: "EN" },
  { value: "fr", flag: "🇫🇷", label: "Français", short: "FR" },
];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365; // 1 year
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function LocaleSelector() {
  const currentLocale = useLocale();
  const { isAuthenticated } = useAuth();
  const updateLocale = useUpdateUserLocale();

  const current = LOCALES.find((l) => l.value === currentLocale) ?? LOCALES[0];

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
        {LOCALES.map((locale) => (
          <DropdownMenuItem
            key={locale.value}
            onClick={() => handleSelect(locale.value)}
            className={currentLocale === locale.value ? "font-semibold" : ""}
          >
            {locale.flag} {locale.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
