import { Card } from "@/components/ui/card";

interface SparklinePoint {
  date: string;
  value: number;
}

interface SparklineCardProps {
  label: string;
  points: SparklinePoint[];
  total?: number;
}

const VIEWBOX_WIDTH = 300;
const VIEWBOX_HEIGHT = 60;

export function SparklineCard({ label, points, total }: SparklineCardProps) {
  const sum = total ?? points.reduce((acc, p) => acc + p.value, 0);
  const max = points.reduce((acc, p) => (p.value > acc ? p.value : acc), 0);

  const path = buildPath(points, max);
  const lastValue = points.length > 0 ? points[points.length - 1].value : 0;

  return (
    <Card className="flex flex-col gap-2 p-5">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-2xl font-bold tabular-nums">
          {sum.toLocaleString("fr-FR")}
        </span>
      </div>
      <svg
        viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
        className="h-16 w-full"
        preserveAspectRatio="none"
        role="img"
        aria-label={`Évolution de ${label}`}
      >
        {max > 0 ? (
          <path
            d={path}
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            className="text-primary"
            vectorEffect="non-scaling-stroke"
          />
        ) : (
          <line
            x1={0}
            x2={VIEWBOX_WIDTH}
            y1={VIEWBOX_HEIGHT / 2}
            y2={VIEWBOX_HEIGHT / 2}
            stroke="currentColor"
            strokeWidth={1}
            strokeDasharray="3 3"
            className="text-muted-foreground/40"
          />
        )}
      </svg>
      <span className="text-xs text-muted-foreground">
        Dernier jour : {lastValue.toLocaleString("fr-FR")}
      </span>
    </Card>
  );
}

function buildPath(points: SparklinePoint[], max: number): string {
  if (points.length === 0 || max === 0) return "";
  const stepX = VIEWBOX_WIDTH / Math.max(points.length - 1, 1);
  return points
    .map((p, i) => {
      const x = i * stepX;
      const y = VIEWBOX_HEIGHT - (p.value / max) * VIEWBOX_HEIGHT;
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}
