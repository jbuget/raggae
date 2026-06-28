"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { McpStatusBadge } from "@/components/atoms/mcp/mcp-status-badge";
import { McpToolsList } from "@/components/molecules/mcp/mcp-tools-list";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import {
  useActivateProjectMcp,
  useDeactivateProjectMcp,
  useProjectMcpActivations,
} from "@/lib/hooks/use-project-mcp-activations";
import type { OrgMcpServerResponse } from "@/lib/types/api";

type ProjectMcpPanelProps = {
  projectId: string;
};

export function ProjectMcpPanel({ projectId }: ProjectMcpPanelProps) {
  const t = useTranslations("projects.settings.mcp");

  const { data: views, isLoading } = useProjectMcpActivations(projectId);
  const activate = useActivateProjectMcp(projectId);
  const deactivate = useDeactivateProjectMcp(projectId);

  const [openServer, setOpenServer] = useState<OrgMcpServerResponse | null>(null);

  function handleToggle(server: OrgMcpServerResponse, isActivated: boolean) {
    if (isActivated) {
      deactivate.mutate(server.id, {
        onSuccess: () => toast.success(t("deactivated")),
        onError: () => toast.error(t("toggleError")),
      });
    } else {
      activate.mutate(server.id, {
        onSuccess: () => toast.success(t("activated")),
        onError: (error) =>
          toast.error((error as Error).message || t("toggleError")),
      });
    }
  }

  return (
    <Card className="space-y-4 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("title")}</h2>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
        <p className="text-xs text-amber-700 dark:text-amber-400">{t("providerWarning")}</p>
      </div>

      {isLoading ? (
        <Skeleton className="h-14 w-full" />
      ) : views?.length ? (
        <div className="space-y-2">
          {views.map((view) => {
            const server = view.org_mcp_server;
            return (
              <div
                key={server.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-md border bg-card p-3"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium">{server.name}</p>
                  <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                    {server.slug}
                  </span>
                  <McpStatusBadge isActive={view.is_activated} />
                  <span className="text-xs text-muted-foreground">
                    {t("toolsCount", { count: server.tools_snapshot.length })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={view.is_activated}
                    disabled={activate.isPending || deactivate.isPending}
                    onCheckedChange={() => handleToggle(server, view.is_activated)}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                    onClick={() => setOpenServer(server)}
                  >
                    {t("viewTools")}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{t("empty")}</p>
      )}

      <Dialog
        open={openServer !== null}
        onOpenChange={(open) => !open && setOpenServer(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {openServer ? t("toolsTitle", { name: openServer.name }) : ""}
            </DialogTitle>
            <DialogDescription>
              {openServer
                ? t("toolsLastRefresh", {
                    date: new Date(openServer.tools_snapshot_at).toLocaleString(),
                  })
                : ""}
            </DialogDescription>
          </DialogHeader>
          {openServer && <McpToolsList tools={openServer.tools_snapshot} />}
        </DialogContent>
      </Dialog>
    </Card>
  );
}
