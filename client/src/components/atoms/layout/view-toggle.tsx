"use client";

import { LayoutGrid, List } from "lucide-react";
import { Button } from "@/components/ui/button";

export type ViewMode = "grid" | "list";

interface ViewToggleProps {
  value: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex items-center rounded-md border">
      <Button
        variant={value === "grid" ? "secondary" : "ghost"}
        size="icon"
        className="h-8 w-8 rounded-r-none border-r"
        onClick={() => onChange("grid")}
      >
        <LayoutGrid className="size-4" />
      </Button>
      <Button
        variant={value === "list" ? "secondary" : "ghost"}
        size="icon"
        className="h-8 w-8 rounded-l-none"
        onClick={() => onChange("list")}
      >
        <List className="size-4" />
      </Button>
    </div>
  );
}
