interface SourceBadgeProps {
  name: string;
  onClick: () => void;
}

export function SourceBadge({ name, onClick }: SourceBadgeProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex cursor-pointer items-center rounded-full border border-border bg-background px-2 py-0.5 text-xs text-muted-foreground transition-colors hover:bg-accent"
    >
      {name}
    </button>
  );
}
