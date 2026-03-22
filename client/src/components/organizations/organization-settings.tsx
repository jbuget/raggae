"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { OrgCredentialsPanel } from "@/components/organizations/org-credentials-panel";
import { OrgDefaultConfigPanel } from "@/components/organizations/org-default-config-panel";
import { OrganizationMembersPanel } from "@/components/organizations/organization-members-panel";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  useDeleteOrganization,
  useOrganization,
  useUpdateOrganization,
} from "@/lib/hooks/use-organization";

const ORG_SETTINGS_TABS = ["General", "Members", "API Keys", "Configuration"] as const;
type OrgSettingsTab = (typeof ORG_SETTINGS_TABS)[number];

type OrganizationSettingsProps = {
  organizationId: string;
};

export function OrganizationSettings({ organizationId }: OrganizationSettingsProps) {
  const t = useTranslations("organizations.settings");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const { data, isLoading, error } = useOrganization(organizationId);
  const deleteOrganization = useDeleteOrganization(organizationId);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<OrgSettingsTab>("General");
  const tabLabels: Record<OrgSettingsTab, string> = {
    General: t("tabGeneral"),
    Members: t("tabMembers"),
    "API Keys": t("tabApiKeys"),
    Configuration: t("tabConfig"),
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-96" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-destructive">{t("loadError")}</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      <div className="flex border-b">
        {ORG_SETTINGS_TABS.map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              type="button"
              role="tab"
              aria-selected={isActive}
              className={[
                "cursor-pointer border-b-2 px-1 py-3 text-sm whitespace-nowrap transition-colors mr-4",
                isActive
                  ? "border-primary text-foreground font-medium"
                  : "border-transparent text-muted-foreground hover:text-foreground",
              ].join(" ")}
              onClick={() => setActiveTab(tab)}
            >
              {tabLabels[tab]}
            </button>
          );
        })}
      </div>

      {activeTab === "General" && (
        <div className="space-y-6">
          <OrganizationProfileForm
            key={`${data.id}-${data.updated_at}`}
            organizationId={organizationId}
            initialName={data.name}
            initialSlug={data.slug}
            initialDescription={data.description}
            initialLogoUrl={data.logo_url}
          />

          <div className="rounded-lg border border-destructive/40 p-5 space-y-3">
            <p className="text-sm font-medium text-destructive">{t("dangerZone")}</p>
            <p className="text-sm text-muted-foreground">
              {t("dangerDescription")}
            </p>
            <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive" disabled={deleteOrganization.isPending}>
                  {t("deleteOrg")}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{t("deleteTitle")}</DialogTitle>
                  <DialogDescription>
                    {t("deleteWarning")}
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setDeleteOpen(false)}>
                    {tCommon("cancel")}
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() =>
                      deleteOrganization.mutate(undefined, {
                        onSuccess: () => {
                          toast.success(t("deleteSuccess"));
                          setDeleteOpen(false);
                          router.push("/organizations");
                        },
                        onError: () => toast.error(t("deleteError")),
                      })
                    }
                    disabled={deleteOrganization.isPending}
                  >
                    {deleteOrganization.isPending ? t("deleting") : t("confirmDelete")}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      )}

      {activeTab === "API Keys" && <OrgCredentialsPanel organizationId={organizationId} />}

      {activeTab === "Members" && <OrganizationMembersPanel organizationId={organizationId} />}

      {activeTab === "Configuration" && (
        <OrgDefaultConfigPanel organizationId={organizationId} />
      )}
    </div>
  );
}

type OrganizationProfileFormProps = {
  organizationId: string;
  initialName: string;
  initialSlug: string | null;
  initialDescription: string | null;
  initialLogoUrl: string | null;
};

function OrganizationProfileForm({
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
