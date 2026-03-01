"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import {
  useActivateOrgModelCredential,
  useCreateOrgModelCredential,
  useDeactivateOrgModelCredential,
  useDeleteOrgModelCredential,
  useOrgModelCredentials,
} from "@/lib/hooks/use-org-model-credentials";
import type { ModelProvider } from "@/lib/types/api";

const PROVIDERS: Array<{ value: ModelProvider; label: string; placeholder: string }> = [
  { value: "openai", label: "OpenAI", placeholder: "sk-..." },
  { value: "gemini", label: "Gemini", placeholder: "AIza..." },
  { value: "anthropic", label: "Anthropic", placeholder: "sk-ant-..." },
];

type OrgCredentialsPanelProps = {
  organizationId: string;
};

export function OrgCredentialsPanel({ organizationId }: OrgCredentialsPanelProps) {
  const { data: credentials, isLoading } = useOrgModelCredentials(organizationId);
  const createCredential = useCreateOrgModelCredential(organizationId);
  const activateCredential = useActivateOrgModelCredential(organizationId);
  const deactivateCredential = useDeactivateOrgModelCredential(organizationId);
  const deleteCredential = useDeleteOrgModelCredential(organizationId);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalProvider, setModalProvider] = useState<ModelProvider>("openai");
  const [modalApiKey, setModalApiKey] = useState("");

  function handleModalOpenChange(open: boolean) {
    setModalOpen(open);
    if (!open) setModalApiKey("");
  }

  function handleSave() {
    const apiKey = modalApiKey.trim();
    if (!apiKey) return;
    createCredential.mutate(
      { provider: modalProvider, api_key: apiKey },
      {
        onSuccess: () => {
          toast.success(`${modalProvider} API key saved`);
          setModalOpen(false);
          setModalApiKey("");
        },
        onError: (error) => {
          toast.error((error as Error).message || "Failed to save API key");
        },
      },
    );
  }

  function handleToggleActive(credentialId: string, currentlyActive: boolean) {
    if (currentlyActive) {
      deactivateCredential.mutate(credentialId, {
        onSuccess: () => toast.success("API key deactivated"),
        onError: (error) => toast.error((error as Error).message || "Failed to deactivate API key"),
      });
    } else {
      activateCredential.mutate(credentialId, {
        onSuccess: () => toast.success("API key activated"),
        onError: () => toast.error("Failed to activate API key"),
      });
    }
  }

  function handleDelete(credentialId: string) {
    deleteCredential.mutate(credentialId, {
      onSuccess: () => toast.success("API key deleted"),
      onError: () => toast.error("Failed to delete API key"),
    });
  }

  const providerPlaceholder =
    PROVIDERS.find((p) => p.value === modalProvider)?.placeholder ?? "";

  return (
    <Card className="space-y-4 p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-lg font-medium">AI provider API keys</h2>
          <p className="text-sm text-muted-foreground">
            Add keys for OpenAI, Gemini, or Anthropic. Only one key per provider can be active at a time.
          </p>
        </div>
        <Button
          type="button"
          className="shrink-0 cursor-pointer"
          onClick={() => setModalOpen(true)}
        >
          Add a key
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-14 w-full" />
      ) : credentials?.length ? (
        <div className="space-y-2">
          {credentials.map((item) => {
            const providerLabel =
              PROVIDERS.find((p) => p.value === item.provider)?.label ?? item.provider;
            return (
              <div
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-3"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-muted px-1.5 py-0.5 text-xs font-medium">
                    {providerLabel}
                  </span>
                  <p className="text-sm font-medium">{item.masked_key}</p>
                  <span className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.is_active
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {item.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={item.is_active}
                    disabled={activateCredential.isPending || deactivateCredential.isPending}
                    onCheckedChange={() => handleToggleActive(item.id, item.is_active)}
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="cursor-pointer"
                    disabled={deleteCredential.isPending}
                    onClick={() => handleDelete(item.id)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No API key saved yet.</p>
      )}

      <Dialog open={modalOpen} onOpenChange={handleModalOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add an API key</DialogTitle>
            <DialogDescription>
              Select a provider then paste your API key.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="org-modal-provider">Provider</Label>
              <select
                id="org-modal-provider"
                value={modalProvider}
                onChange={(e) => setModalProvider(e.target.value as ModelProvider)}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {PROVIDERS.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="org-modal-api-key">API key</Label>
              <Input
                id="org-modal-api-key"
                type="password"
                placeholder={providerPlaceholder}
                value={modalApiKey}
                onChange={(e) => setModalApiKey(e.target.value)}
                autoComplete="off"
              />
            </div>
          </div>

          <DialogFooter showCloseButton>
            <Button
              type="button"
              className="cursor-pointer"
              disabled={!modalApiKey.trim() || createCredential.isPending}
              onClick={handleSave}
            >
              Save key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
