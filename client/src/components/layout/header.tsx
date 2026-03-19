"use client";

import Link from "next/link";
import { signOut } from "next-auth/react";
import { useLocale, useTranslations } from "next-intl";
import { Check, Languages, LogOut, Monitor, Moon, Settings, Sun } from "lucide-react";
import type { Theme } from "@/lib/providers/theme-provider";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useAuth } from "@/lib/hooks/use-auth";
import { useTheme } from "@/lib/providers/theme-provider";
import { useUpdateUserLocale } from "@/lib/hooks/use-user-profile";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";
import { MobileSidebar } from "./mobile-sidebar";

const LOCALES: Array<{ value: UpdateUserLocaleRequest["locale"]; label: string }> = [
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365;
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function Header() {
  const { user } = useAuth();
  const t = useTranslations("header");
  const tTheme = useTranslations("layout.themeToggle");
  const { theme, setTheme } = useTheme();

  const THEMES: Array<{ value: Theme; label: string; icon: React.ReactNode }> = [
    { value: "light", label: tTheme("light"), icon: <Sun size={14} /> },
    { value: "dark", label: tTheme("dark"), icon: <Moon size={14} /> },
    { value: "system", label: tTheme("system"), icon: <Monitor size={14} /> },
  ];
  const currentLocale = useLocale();
  const updateLocale = useUpdateUserLocale();

  function handleThemeSelect(next: Theme) {
    if (next !== theme) setTheme(next);
  }

  function handleLocaleSelect(locale: UpdateUserLocaleRequest["locale"]) {
    if (locale === currentLocale) return;
    setLocaleCookie(locale);
    updateLocale.mutate({ locale }, { onSettled: () => window.location.reload() });
  }

  return (
    <header className="flex h-14 items-center justify-between border-b px-6">
      <div className="flex items-center gap-4">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="sm" className="md:hidden">
              {t("account")}
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <MobileSidebar />
          </SheetContent>
        </Sheet>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="cursor-pointer">
              {user?.email ?? t("account")}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52">
            <DropdownMenuItem disabled className="text-muted-foreground text-xs">
              {user?.email}
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <Link href="/settings" className="flex cursor-pointer items-center gap-2">
                <Settings size={14} />
                {t("userSettings")}
              </Link>
            </DropdownMenuItem>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex cursor-pointer items-center gap-2">
                <Languages size={14} />
                {t("language")}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {LOCALES.map(({ value, label }) => (
                  <DropdownMenuItem
                    key={value}
                    onClick={() => handleLocaleSelect(value)}
                    className="flex cursor-pointer items-center gap-2"
                  >
                    <Check
                      size={14}
                      className={currentLocale === value ? "opacity-100" : "opacity-0"}
                    />
                    {label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex cursor-pointer items-center gap-2">
                <Sun size={14} />
                {tTheme("label")}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {THEMES.map(({ value, label, icon }) => (
                  <DropdownMenuItem
                    key={value}
                    onClick={() => handleThemeSelect(value)}
                    className="flex cursor-pointer items-center gap-2"
                  >
                    <Check
                      size={14}
                      className={theme === value ? "opacity-100" : "opacity-0"}
                    />
                    {icon}
                    {label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSeparator />

            <DropdownMenuItem
              onClick={() => signOut({ callbackUrl: "/login" })}
              className="flex cursor-pointer items-center gap-2"
            >
              <LogOut size={14} />
              {t("signOut")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
