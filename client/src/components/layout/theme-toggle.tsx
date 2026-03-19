"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/lib/providers/theme-provider";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const t = useTranslations("layout.themeToggle");
  const isDark = theme === "dark" || (theme === "system" && typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  return (
    <Button
      variant="ghost"
      size="sm"
      className="cursor-pointer"
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label={isDark ? t("switchToLight") : t("switchToDark")}
    >
      {isDark ? t("light") : t("dark")}
    </Button>
  );
}
