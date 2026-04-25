import type * as React from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface FieldInputProps extends React.ComponentProps<"input"> {
  label: string;
  hint?: string;
  labelExtra?: React.ReactNode;
  id: string;
}

export function FieldInput({ label, hint, labelExtra, id, className, ...props }: FieldInputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label htmlFor={id}>{label}</Label>
        {labelExtra}
      </div>
      <Input id={id} className={className} {...props} />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
