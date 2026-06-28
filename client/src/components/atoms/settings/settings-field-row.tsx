import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type SettingsFieldRowProps = {
  label: ReactNode;
  description?: string;
  hint?: ReactNode;
  dirty?: boolean;
  children: ReactNode;
};

export function SettingsFieldRow({ label, description, hint, dirty, children }: SettingsFieldRowProps) {
  return (
    <div className={cn(
      "grid grid-cols-2 gap-6 rounded-md px-3 py-2.5 transition-colors hover:bg-white/5",
      dirty && "bg-blue-50/60 dark:bg-blue-950/10",
    )}>
      <div className={cn(
        "border-l-2 pl-3 space-y-1",
        dirty ? "border-l-blue-200/50" : "border-l-border",
      )}>
        {label}
        {description && (
          <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
        )}
      </div>
      <div className="flex flex-col gap-1">
        <div className="flex items-center">
          {children}
        </div>
        {hint}
      </div>
    </div>
  );
}
