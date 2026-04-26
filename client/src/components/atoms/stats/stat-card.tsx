import { Card } from "@/components/ui/card";

export function StatCard({
  label,
  value,
  unit,
}: {
  label: string;
  value: string | number;
  unit?: string;
}) {
  return (
    <Card className="flex flex-col gap-1 p-5">
      <span className="text-2xl font-bold tabular-nums">
        {value}
        {unit && <span className="ml-1 text-base font-normal text-muted-foreground">{unit}</span>}
      </span>
      <span className="text-sm text-muted-foreground">{label}</span>
    </Card>
  );
}
