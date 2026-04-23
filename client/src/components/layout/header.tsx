"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { MobileSidebar } from "./sidebar";

export function Header() {
  const t = useTranslations("header");

  return (
    <header className="flex h-14 items-center border-b px-6 md:hidden">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="sm">
            {t("account")}
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <MobileSidebar />
        </SheetContent>
      </Sheet>
    </header>
  );
}
