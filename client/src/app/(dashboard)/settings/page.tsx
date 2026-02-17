"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useActivateModelCredential,
  useCreateModelCredential,
  useDeleteModelCredential,
  useModelCredentials,
} from "@/lib/hooks/use-model-credentials";
import type { ModelProvider } from "@/lib/types/api";

const PROVIDERS: Array<{ value: ModelProvider; label: string; placeholder: string }> = [
  { value: "openai", label: "OpenAI", placeholder: "sk-..." },
  { value: "gemini", label: "Gemini", placeholder: "AIza..." },
  { value: "anthropic", label: "Anthropic", placeholder: "sk-ant-..." },
];

export default function UserSettingsPage() {
  const { data: credentials, isLoading } = useModelCredentials();
  const createCredential = useCreateModelCredential();
  const activateCredential = useActivateModelCredential();
  const deleteCredential = useDeleteModelCredential();
  const [draftValues, setDraftValues] = useState<Record<ModelProvider, string>>({
    openai: "",
    gemini: "",
    anthropic: "",
  });

  const credentialsByProvider = useMemo(() => {
    const grouped: Record<ModelProvider, typeof credentials> = {
      openai: [],
      gemini: [],
      anthropic: [],
    };
    for (const item of credentials ?? []) {
      grouped[item.provider].push(item);
    }
    return grouped;
  }, [credentials]);

  function setDraft(provider: ModelProvider, value: string) {
    setDraftValues((prev) => ({ ...prev, [provider]: value }));
  }

  function handleSave(provider: ModelProvider) {
    const apiKey = draftValues[provider].trim();
    if (!apiKey) return;

    createCredential.mutate(
      { provider, api_key: apiKey },
      {
        onSuccess: () => {
          toast.success(`${provider} API key saved`);
          setDraft(provider, "");
        },
        onError: (error) => {
          toast.error((error as Error).message || "Failed to save API key");
        },
      },
    );
  }

  function handleActivate(credentialId: string) {
    activateCredential.mutate(credentialId, {
      onSuccess: () => toast.success("API key activated"),
      onError: () => toast.error("Failed to activate API key"),
    });
  }

  function handleDelete(credentialId: string) {
    deleteCredential.mutate(credentialId, {
      onSuccess: () => toast.success("API key deleted"),
      onError: () => toast.error("Failed to delete API key"),
    });
  }

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">User Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Configure your provider API keys for OpenAI, Gemini, and Anthropic.
        </p>
      </div>

      {PROVIDERS.map((provider) => (
        <Card key={provider.value} className="space-y-4 p-5">
          <div className="space-y-1">
            <h2 className="text-lg font-medium">{provider.label}</h2>
            <p className="text-sm text-muted-foreground">
              Add a key and choose which one is active for this provider.
            </p>
          </div>

          <div className="grid gap-2 sm:grid-cols-[1fr_auto] sm:items-end">
            <div className="space-y-2">
              <Label htmlFor={`api-key-${provider.value}`}>API key</Label>
              <Input
                id={`api-key-${provider.value}`}
                type="password"
                value={draftValues[provider.value]}
                onChange={(event) => setDraft(provider.value, event.target.value)}
                placeholder={provider.placeholder}
                autoComplete="off"
              />
            </div>
            <Button
              type="button"
              className="cursor-pointer"
              onClick={() => handleSave(provider.value)}
              disabled={!draftValues[provider.value].trim() || createCredential.isPending}
            >
              Save key
            </Button>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium">Existing keys</p>
            {isLoading ? (
              <Skeleton className="h-14 w-full" />
            ) : credentialsByProvider[provider.value]?.length ? (
              <div className="space-y-2">
                {credentialsByProvider[provider.value].map((item) => (
                  <div
                    key={item.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-3"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{item.masked_key}</p>
                      <p className="text-xs text-muted-foreground">
                        {item.is_active ? "Active" : "Inactive"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        className="cursor-pointer"
                        disabled={item.is_active || activateCredential.isPending}
                        onClick={() => handleActivate(item.id)}
                      >
                        Activate
                      </Button>
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
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No key saved for {provider.label}.</p>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
