"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface SidebarNavLinkProps {
  href: string;
  label: string;
  icon?: React.ReactNode;
  matchPrefix?: boolean;
}

export function SidebarNavLink({ href, label, icon, matchPrefix = false }: SidebarNavLinkProps) {
  const pathname = usePathname();
  const isActive = matchPrefix ? pathname.startsWith(href) : pathname === href;

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
    >
      {icon}
      {label}
    </Link>
  );
}
