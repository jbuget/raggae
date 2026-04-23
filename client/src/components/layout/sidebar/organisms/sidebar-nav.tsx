"use client";

import { Building2, FolderOpen, Mail } from "lucide-react";
import { useTranslations } from "next-intl";
import { SidebarNavLink } from "../atoms/sidebar-nav-link";

interface SidebarNavProps {
  showIcons?: boolean;
  matchPrefix?: boolean;
}

export function SidebarNav({ showIcons = false, matchPrefix = false }: SidebarNavProps) {
  const tNav = useTranslations("nav");

  const navItems = [
    { href: "/projects", label: tNav("projects"), icon: showIcons ? <FolderOpen size={16} /> : undefined },
    { href: "/organizations", label: tNav("organizations"), icon: showIcons ? <Building2 size={16} /> : undefined },
    { href: "/invitations", label: tNav("invitations"), icon: showIcons ? <Mail size={16} /> : undefined },
  ];

  return (
    <div className="space-y-1">
      {navItems.map((item) => (
        <SidebarNavLink
          key={item.href}
          href={item.href}
          label={item.label}
          icon={item.icon}
          matchPrefix={matchPrefix}
        />
      ))}
    </div>
  );
}
