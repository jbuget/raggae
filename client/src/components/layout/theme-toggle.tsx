"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/lib/providers/theme-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const t = useTranslations("layout.themeToggle");

  return (
    <Button
      variant="ghost"
      size="sm"
      className="cursor-pointer"
      onClick={toggleTheme}
      aria-label={theme === "light" ? t("switchToDark") : t("switchToLight")}
    >
      {theme === "light" ? t("dark") : t("light")}
    </Button>
  );
}
