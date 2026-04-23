import Link from "next/link";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SidebarSectionHeaderProps {
  title: string;
  canCreate?: boolean;
  createHref?: string;
  createAriaLabel?: string;
}

export function SidebarSectionHeader({
  title,
  canCreate = false,
  createHref,
  createAriaLabel,
}: SidebarSectionHeaderProps) {
  return (
    <div className="flex h-6 items-center justify-between px-1 pb-1">
      <p
        className="truncate px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground"
        title={title}
      >
        {title}
      </p>
      {canCreate && createHref && (
        <Button asChild variant="ghost" size="icon" className="h-7 w-7">
          <Link href={createHref} aria-label={createAriaLabel}>
            <Plus className="h-4 w-4" />
          </Link>
        </Button>
      )}
    </div>
  );
}
