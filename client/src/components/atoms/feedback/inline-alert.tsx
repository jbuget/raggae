import { Info, Loader2, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

interface InlineAlertProps {
  variant?: "warning" | "info" | "loading";
  children: React.ReactNode;
  className?: string;
}

const VARIANTS = {
  warning: {
    container: "border-yellow-500/40 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400",
    icon: TriangleAlert,
    spin: false,
  },
  info: {
    container: "border-blue-500/40 bg-blue-500/10 text-blue-700 dark:text-blue-400",
    icon: Info,
    spin: false,
  },
  loading: {
    container: "border-blue-500/40 bg-blue-500/10 text-blue-700 dark:text-blue-400",
    icon: Loader2,
    spin: true,
  },
};

export function InlineAlert({ variant = "warning", children, className }: InlineAlertProps) {
  const { container, icon: Icon, spin } = VARIANTS[variant];
  return (
    <div className={cn("flex items-start gap-2 rounded-md border px-3 py-2.5 text-sm", container, className)}>
      <Icon className={cn("mt-0.5 size-4 shrink-0", spin && "animate-spin")} />
      <span>{children}</span>
    </div>
  );
}
