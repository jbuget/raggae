import type { ReactNode } from "react";

type BreadcrumbItem = {
  label: ReactNode;
  href?: string;
};

type WorkspaceTemplateProps = {
  breadcrumb: BreadcrumbItem[];
  actions?: ReactNode;
  children: ReactNode;
};

export function WorkspaceTemplate({ breadcrumb, actions, children }: WorkspaceTemplateProps) {
  return (
    <div className="-m-6 flex h-screen flex-col">
      <div className="flex h-14 shrink-0 items-center justify-between border-b px-6">
        <div className="flex items-center gap-2 text-sm">
          {breadcrumb.map((item, index) => (
            <span key={index} className="flex items-center gap-2">
              {index > 0 && <span className="text-muted-foreground">›</span>}
              <span className={index === breadcrumb.length - 1 ? "text-muted-foreground" : "font-bold"}>
                {item.label}
              </span>
            </span>
          ))}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      <div className="min-h-0 flex-1">{children}</div>
    </div>
  );
}
