"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useUpdateOrganization } from "@/lib/hooks/use-organization";

interface OrganizationProfileFormProps {
  organizationId: string;
  initialName: string;
  initialSlug: string | null;
  initialDescription: string | null;
  initialLogoUrl: string | null;
}

export function OrganizationProfileForm({
  organizationId,
  initialName,
  initialSlug,
  initialDescription,
  initialLogoUrl,
}: OrganizationProfileFormProps) {
  const t = useTranslations("organizations.settings");
  const tCommon = useTranslations("common");
  const updateOrganization = useUpdateOrganization(organizationId);
  const [name, setName] = useState(initialName);
  const [slug, setSlug] = useState(initialSlug ?? "");
  const [description, setDescription] = useState(initialDescription ?? "");
  const [logoUrl, setLogoUrl] = useState(initialLogoUrl ?? "");

  return (
    <div className="rounded-lg border p-5 space-y-4">
      <div className="space-y-2">
        <Label htmlFor="org-name">{t("nameLabel")}</Label>
        <Input id="org-name" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-slug">{t("slugLabel")}</Label>
        <Input id="org-slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-description">{t("descriptionLabel")}</Label>
        <Textarea
          id="org-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-logo-url">{t("logoLabel")}</Label>
        <Input
          id="org-logo-url"
          value={logoUrl}
          onChange={(e) => setLogoUrl(e.target.value)}
        />
      </div>
      <Button
        onClick={() =>
          updateOrganization.mutate(
            {
              name: name.trim(),
              slug: slug.trim() || null,
              description: description.trim() || null,
              logo_url: logoUrl.trim() || null,
            },
            {
              onSuccess: () => toast.success(t("updateSuccess")),
              onError: () => toast.error(t("updateError")),
            },
          )
        }
        disabled={updateOrganization.isPending || !name.trim()}
      >
        {updateOrganization.isPending ? tCommon("saving") : tCommon("save")}
      </Button>
    </div>
  );
}
