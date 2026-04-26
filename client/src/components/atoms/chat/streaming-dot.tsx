interface StreamingDotProps {
  delay: number;
}

export function StreamingDot({ delay }: StreamingDotProps) {
  return (
    <span
      role="presentation"
      className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"
      style={{ animationDelay: `${delay}ms` }}
    />
  );
}
