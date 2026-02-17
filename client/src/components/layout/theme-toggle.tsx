"use client";

import { Button } from "@/components/ui/button";
import { useTheme } from "@/lib/providers/theme-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="sm"
      className="cursor-pointer"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
    >
      {theme === "light" ? "Dark" : "Light"}
    </Button>
  );
}
