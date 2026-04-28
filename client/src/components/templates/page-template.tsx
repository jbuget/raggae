import type { ReactNode } from "react";

type PageTemplateProps = {
  title: ReactNode;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function PageTemplate({ title, description, actions, children }: PageTemplateProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">{title}</h1>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        {actions && <div className="shrink-0">{actions}</div>}
      </div>
      {children}
    </div>
  );
}
