"use client";

import Link from "next/link";
import { signOut } from "next-auth/react";
import { BarChart2, Check, Languages, LogOut, Monitor, Moon, Settings, Sun } from "lucide-react";
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
            <Link href="/stats" className="flex cursor-pointer items-center gap-2">
              <BarChart2 size={14} />
              {t("stats")}
            </Link>
          </DropdownMenuItem>

          <DropdownMenuItem asChild>
            <a
              href="https://github.com/jbuget/raggae"
              target="_blank"
              rel="noreferrer"
              className="flex cursor-pointer items-center gap-2"
            >
              <svg
                width={14}
                height={14}
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 .5C5.65.5.5 5.65.5 12a11.5 11.5 0 0 0 7.86 10.92c.57.1.78-.25.78-.55v-1.95c-3.2.7-3.87-1.54-3.87-1.54-.52-1.33-1.28-1.68-1.28-1.68-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.58.24 2.75.12 3.04.74.81 1.18 1.83 1.18 3.09 0 4.42-2.69 5.39-5.26 5.68.41.35.78 1.05.78 2.12v3.14c0 .3.21.66.79.55A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z" />
              </svg>
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
