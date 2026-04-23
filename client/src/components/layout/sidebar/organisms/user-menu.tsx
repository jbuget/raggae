"use client";

import Link from "next/link";
import { signOut } from "next-auth/react";
import { Check, Github, Languages, LogOut, Monitor, Moon, Settings, Sun } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
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
import { useAuth } from "@/lib/hooks/use-auth";
import { useUpdateUserLocale } from "@/lib/hooks/use-user-profile";
import type { Theme } from "@/lib/providers/theme-provider";
import { useTheme } from "@/lib/providers/theme-provider";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";

const LOCALES: Array<{ value: UpdateUserLocaleRequest["locale"]; label: string }> = [
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365;
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function UserMenu() {
  const { user } = useAuth();
  const tHeader = useTranslations("header");
  const t = useTranslations("sidebar");
  const tTheme = useTranslations("layout.themeToggle");
  const { theme, setTheme } = useTheme();
  const currentLocale = useLocale();
  const updateLocale = useUpdateUserLocale();

  const THEMES: Array<{ value: Theme; label: string; icon: React.ReactNode }> = [
    { value: "light", label: tTheme("light"), icon: <Sun size={14} /> },
    { value: "dark", label: tTheme("dark"), icon: <Moon size={14} /> },
    { value: "system", label: tTheme("system"), icon: <Monitor size={14} /> },
  ];

  const gitBranch = process.env.NEXT_PUBLIC_APP_GIT_BRANCH ?? "unknown";
  const gitCommit = process.env.NEXT_PUBLIC_APP_GIT_COMMIT ?? "unknown";
  const shortCommit = gitCommit === "unknown" ? gitCommit : gitCommit.slice(0, 7);

  function handleThemeSelect(next: Theme) {
    if (next !== theme) setTheme(next);
  }

  function handleLocaleSelect(locale: UpdateUserLocaleRequest["locale"]) {
    if (locale === currentLocale) return;
    setLocaleCookie(locale);
    updateLocale.mutate({ locale }, { onSettled: () => window.location.reload() });
  }

  return (
    <div className="border-t p-3">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="w-full cursor-pointer justify-start truncate">
            {user?.email ?? tHeader("account")}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent side="top" align="start" className="w-52">
          <DropdownMenuItem disabled className="text-xs text-muted-foreground">
            {user?.email}
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem asChild>
            <Link href="/settings" className="flex cursor-pointer items-center gap-2">
              <Settings size={14} />
              {tHeader("userSettings")}
            </Link>
          </DropdownMenuItem>

          <DropdownMenuSub>
            <DropdownMenuSubTrigger className="flex cursor-pointer items-center gap-2">
              <Languages size={14} />
              {tHeader("language")}
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

          <DropdownMenuItem asChild>
            <a
              href="https://github.com/jbuget/raggae"
              target="_blank"
              rel="noreferrer"
              className="flex cursor-pointer items-center gap-2"
            >
              <Github size={14} />
              {t("sourceCode")}
            </a>
          </DropdownMenuItem>

          <DropdownMenuItem disabled className="text-xs text-muted-foreground">
            {gitBranch}@{shortCommit}
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            onClick={() => signOut({ callbackUrl: "/login" })}
            className="flex cursor-pointer items-center gap-2"
          >
            <LogOut size={14} />
            {tHeader("signOut")}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
