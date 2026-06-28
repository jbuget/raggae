"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { McpStatusBadge } from "@/components/atoms/mcp/mcp-status-badge";
import { McpServerForm } from "@/components/molecules/mcp/mcp-server-form";
import { McpToolsList } from "@/components/molecules/mcp/mcp-tools-list";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import {
  useActivateOrgMcpServer,
  useDeactivateOrgMcpServer,
  useDeclareOrgMcpServer,
  useDeleteOrgMcpServer,
  useOrgMcpServers,
  useRefreshOrgMcpTools,
} from "@/lib/hooks/use-org-mcp-servers";
import type { OrgMcpServerResponse } from "@/lib/types/api";

type OrgMcpListProps = {
  organizationId: string;
};

export function OrgMcpList({ organizationId }: OrgMcpListProps) {
  const t = useTranslations("organizations.mcpServers");

  const { data: servers, isLoading } = useOrgMcpServers(organizationId);
  const declareServer = useDeclareOrgMcpServer(organizationId);
  const activateServer = useActivateOrgMcpServer(organizationId);
  const deactivateServer = useDeactivateOrgMcpServer(organizationId);
  const deleteServer = useDeleteOrgMcpServer(organizationId);
  const refreshTools = useRefreshOrgMcpTools(organizationId);

  const [declareOpen, setDeclareOpen] = useState(false);
  const [openToolsServerId, setOpenToolsServerId] = useState<string | null>(null);

  function handleDeclare(data: Parameters<typeof declareServer.mutate>[0]) {
    declareServer.mutate(data, {
      onSuccess: () => {
        toast.success(t("declareSuccess"));
        setDeclareOpen(false);
      },
      onError: (error) =>
        toast.error((error as Error).message || t("declareError")),
    });
  }

  function handleToggle(server: OrgMcpServerResponse) {
    if (server.is_active) {
      deactivateServer.mutate(server.id, {
        onSuccess: () => toast.success(t("deactivated")),
        onError: () => toast.error(t("toggleError")),
      });
    } else {
      activateServer.mutate(server.id, {
        onSuccess: () => toast.success(t("activated")),
        onError: () => toast.error(t("toggleError")),
      });
    }
  }

  function handleRefresh(server: OrgMcpServerResponse) {
    refreshTools.mutate(server.id, {
      onSuccess: () => toast.success(t("refreshed")),
      onError: (error) =>
        toast.error((error as Error).message || t("refreshError")),
    });
  }

  function handleDelete(server: OrgMcpServerResponse) {
    deleteServer.mutate(server.id, {
      onSuccess: () => toast.success(t("deleted")),
      onError: () => toast.error(t("deleteError")),
    });
  }

  const openToolsServer =
    openToolsServerId !== null
      ? servers?.find((s) => s.id === openToolsServerId)
      : null;

  return (
    <Card className="space-y-4 p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-lg font-medium">{t("title")}</h2>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>
        <Button
          type="button"
          className="shrink-0 cursor-pointer"
          onClick={() => setDeclareOpen(true)}
        >
          {t("declareCta")}
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-14 w-full" />
      ) : servers?.length ? (
        <div className="space-y-2">
          {servers.map((server) => (
            <div
              key={server.id}
              className="space-y-2 rounded-md border bg-card p-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium">{server.name}</p>
                  <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                    {server.slug}
                  </span>
                  <McpStatusBadge isActive={server.is_active} />
                  {server.masked_token && (
                    <span className="font-mono text-xs text-muted-foreground">
                      {server.masked_token}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={server.is_active}
                    disabled={
                      activateServer.isPending || deactivateServer.isPending
                    }
                    onCheckedChange={() => handleToggle(server)}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                    disabled={refreshTools.isPending}
                    onClick={() => handleRefresh(server)}
                  >
                    {t("refresh")}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                    onClick={() => setOpenToolsServerId(server.id)}
                  >
                    {t("viewTools", { count: server.tools_snapshot.length })}
                  </Button>
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="cursor-pointer"
                    disabled={deleteServer.isPending}
                    onClick={() => handleDelete(server)}
                  >
                    {t("delete")}
                  </Button>
                </div>
              </div>
              <p className="break-all font-mono text-xs text-muted-foreground">
                {server.url}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{t("empty")}</p>
      )}

      <Dialog open={declareOpen} onOpenChange={setDeclareOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("declareTitle")}</DialogTitle>
            <DialogDescription>{t("declareDescription")}</DialogDescription>
          </DialogHeader>
          <McpServerForm
            submitLabel={t("declareCta")}
            isSubmitting={declareServer.isPending}
            onSubmit={handleDeclare}
            onCancel={() => setDeclareOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog
        open={openToolsServer !== null && openToolsServer !== undefined}
        onOpenChange={(open) => !open && setOpenToolsServerId(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {openToolsServer ? t("toolsTitle", { name: openToolsServer.name }) : ""}
            </DialogTitle>
            <DialogDescription>
              {openToolsServer
                ? t("toolsLastRefresh", {
                    date: new Date(
                      openToolsServer.tools_snapshot_at,
                    ).toLocaleString(),
                  })
                : ""}
            </DialogDescription>
          </DialogHeader>
          {openToolsServer && <McpToolsList tools={openToolsServer.tools_snapshot} />}
        </DialogContent>
      </Dialog>
    </Card>
  );
}
