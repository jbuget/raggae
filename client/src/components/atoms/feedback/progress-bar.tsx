import { cn } from "@/lib/utils";

type ProgressBarVariant = "default" | "warning" | "danger";
type ProgressBarSize = "sm" | "md";

interface ProgressBarProps {
  value: number;
  max: number;
  variant?: ProgressBarVariant;
  size?: ProgressBarSize;
  label?: string;
  className?: string;
}

const VARIANTS: Record<ProgressBarVariant, string> = {
  default: "bg-primary",
  warning: "bg-amber-500",
  danger: "bg-red-600",
};

const SIZES: Record<ProgressBarSize, string> = {
  sm: "h-0.5",
  md: "h-1.5",
};

export function ProgressBar({
  value,
  max,
  variant = "default",
  size = "md",
  label,
  className,
}: ProgressBarProps) {
  const ratio = Math.min(Math.max(max > 0 ? value / max : 0, 0), 1);
  return (
    <div
      className={cn("w-full overflow-hidden rounded-full bg-muted", SIZES[size], className)}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={label}
    >
      <div
        className={cn("h-full rounded-full transition-all duration-300", VARIANTS[variant])}
        style={{ width: `${ratio * 100}%` }}
      />
    </div>
  );
}
