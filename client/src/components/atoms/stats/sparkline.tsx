"use client";

import { useMemo, useRef, useState } from "react";
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

  const svgRef = useRef<SVGSVGElement | null>(null);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const { path, areaPath, coords } = useMemo(
    () => buildGeometry(points, max),
    [points, max],
  );

  const lastValue = points.length > 0 ? points[points.length - 1].value : 0;
  const hovered = hoverIndex !== null ? points[hoverIndex] : null;
  const hoveredCoord = hoverIndex !== null ? coords[hoverIndex] : null;

  function handleMove(event: React.MouseEvent<SVGSVGElement>) {
    if (points.length === 0 || max === 0) return;
    const svg = svgRef.current;
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const relativeX = ((event.clientX - rect.left) / rect.width) * VIEWBOX_WIDTH;
    const stepX = VIEWBOX_WIDTH / Math.max(points.length - 1, 1);
    const index = Math.round(relativeX / stepX);
    const clamped = Math.min(Math.max(index, 0), points.length - 1);
    setHoverIndex(clamped);
  }

  function handleLeave() {
    setHoverIndex(null);
  }

  return (
    <Card className="flex flex-col gap-2 p-5">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-2xl font-bold tabular-nums">
          {sum.toLocaleString("fr-FR")}
        </span>
      </div>
      <div className="relative">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
          className="h-16 w-full cursor-crosshair"
          preserveAspectRatio="none"
          role="img"
          aria-label={`Évolution de ${label}`}
          onMouseMove={handleMove}
          onMouseLeave={handleLeave}
        >
          {max > 0 ? (
            <>
              <path
                d={areaPath}
                fill="currentColor"
                className="text-primary/10"
                vectorEffect="non-scaling-stroke"
              />
              <path
                d={path}
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                className="text-primary"
                vectorEffect="non-scaling-stroke"
              />
              {hoveredCoord && (
                <>
                  <line
                    x1={hoveredCoord.x}
                    x2={hoveredCoord.x}
                    y1={0}
                    y2={VIEWBOX_HEIGHT}
                    stroke="currentColor"
                    strokeWidth={1}
                    strokeDasharray="2 2"
                    className="text-muted-foreground"
                    vectorEffect="non-scaling-stroke"
                  />
                  <circle
                    cx={hoveredCoord.x}
                    cy={hoveredCoord.y}
                    r={3}
                    className="fill-background stroke-primary"
                    strokeWidth={1.5}
                    vectorEffect="non-scaling-stroke"
                  />
                </>
              )}
            </>
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
        {hovered && hoveredCoord && (
          <div
            className="pointer-events-none absolute -top-2 z-10 -translate-x-1/2 -translate-y-full rounded-md border bg-popover px-2 py-1 text-xs text-popover-foreground shadow-md"
            style={{ left: `${(hoveredCoord.x / VIEWBOX_WIDTH) * 100}%` }}
            role="tooltip"
          >
            <div className="font-semibold tabular-nums">
              {hovered.value.toLocaleString("fr-FR")}
            </div>
            <div className="text-muted-foreground">{formatDate(hovered.date)}</div>
          </div>
        )}
      </div>
      <span className="text-xs text-muted-foreground">
        Dernier jour : {lastValue.toLocaleString("fr-FR")}
      </span>
    </Card>
  );
}

interface Coord {
  x: number;
  y: number;
}

interface Geometry {
  path: string;
  areaPath: string;
  coords: Coord[];
}

function buildGeometry(points: SparklinePoint[], max: number): Geometry {
  if (points.length === 0 || max === 0) {
    return { path: "", areaPath: "", coords: [] };
  }
  const stepX = VIEWBOX_WIDTH / Math.max(points.length - 1, 1);
  const coords: Coord[] = points.map((p, i) => ({
    x: i * stepX,
    y: VIEWBOX_HEIGHT - (p.value / max) * VIEWBOX_HEIGHT,
  }));
  const path = coords
    .map((c, i) => `${i === 0 ? "M" : "L"}${c.x.toFixed(2)},${c.y.toFixed(2)}`)
    .join(" ");
  const firstX = coords[0].x.toFixed(2);
  const lastX = coords[coords.length - 1].x.toFixed(2);
  const areaPath = `${path} L${lastX},${VIEWBOX_HEIGHT} L${firstX},${VIEWBOX_HEIGHT} Z`;
  return { path, areaPath, coords };
}

function formatDate(iso: string): string {
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return iso;
  return parsed.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
