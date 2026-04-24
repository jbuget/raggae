import type * as React from "react";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface FieldTextareaProps extends React.ComponentProps<"textarea"> {
  label: string;
  hint?: string;
  labelExtra?: React.ReactNode;
  id: string;
}

export function FieldTextarea({ label, hint, labelExtra, id, ...props }: FieldTextareaProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label htmlFor={id}>{label}</Label>
        {labelExtra}
      </div>
      <Textarea id={id} {...props} />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
