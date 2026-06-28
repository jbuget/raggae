"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type {
  DeclareOrgMcpServerRequest,
  McpAuthType,
} from "@/lib/types/api";

const MIN_TIMEOUT = 5;
const MAX_TIMEOUT = 60;

type McpServerFormProps = {
  initialName?: string;
  initialUrl?: string;
  initialAuthType?: McpAuthType;
  initialTimeoutSeconds?: number;
  submitLabel: string;
  isSubmitting: boolean;
  onSubmit: (data: DeclareOrgMcpServerRequest) => void;
  onCancel: () => void;
};

export function McpServerForm({
  initialName = "",
  initialUrl = "",
  initialAuthType = "none",
  initialTimeoutSeconds = 30,
  submitLabel,
  isSubmitting,
  onSubmit,
  onCancel,
}: McpServerFormProps) {
  const t = useTranslations("organizations.mcpServers");
  const tCommon = useTranslations("common");

  const [name, setName] = useState(initialName);
  const [url, setUrl] = useState(initialUrl);
  const [authType, setAuthType] = useState<McpAuthType>(initialAuthType);
  const [bearerToken, setBearerToken] = useState("");
  const [timeoutSeconds, setTimeoutSeconds] = useState(initialTimeoutSeconds);

  const canSubmit =
    name.trim().length > 0 &&
    url.trim().startsWith("https://") &&
    timeoutSeconds >= MIN_TIMEOUT &&
    timeoutSeconds <= MAX_TIMEOUT &&
    (authType === "none" || bearerToken.trim().length > 0);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit({
      name: name.trim(),
      url: url.trim(),
      auth_type: authType,
      bearer_token: authType === "bearer" ? bearerToken.trim() : null,
      timeout_seconds: timeoutSeconds,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="mcp-name">{t("nameLabel")}</Label>
        <Input
          id="mcp-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={t("namePlaceholder")}
          autoComplete="off"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="mcp-url">{t("urlLabel")}</Label>
        <Input
          id="mcp-url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://mcp.example.com/"
          autoComplete="off"
        />
        <p className="text-xs text-muted-foreground">{t("urlHint")}</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="mcp-auth-type">{t("authLabel")}</Label>
        <Select
          value={authType}
          onValueChange={(val) => setAuthType(val as McpAuthType)}
        >
          <SelectTrigger id="mcp-auth-type">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">{t("authNone")}</SelectItem>
            <SelectItem value="bearer">{t("authBearer")}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {authType === "bearer" && (
        <div className="space-y-2">
          <Label htmlFor="mcp-bearer">{t("tokenLabel")}</Label>
          <Input
            id="mcp-bearer"
            type="password"
            value={bearerToken}
            onChange={(e) => setBearerToken(e.target.value)}
            placeholder={t("tokenPlaceholder")}
            autoComplete="off"
          />
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="mcp-timeout">{t("timeoutLabel")}</Label>
        <Input
          id="mcp-timeout"
          type="number"
          min={MIN_TIMEOUT}
          max={MAX_TIMEOUT}
          value={timeoutSeconds}
          onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
        />
        <p className="text-xs text-muted-foreground">
          {t("timeoutHint", { min: MIN_TIMEOUT, max: MAX_TIMEOUT })}
        </p>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          {tCommon("cancel")}
        </Button>
        <Button type="submit" disabled={!canSubmit || isSubmitting}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
