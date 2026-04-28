"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { OrganizationProfileForm } from "@/components/molecules/organization/organization-profile-form";
import { OrgCredentialsPanel } from "@/components/organisms/organization/org-credentials-panel";
import { OrganizationMembersPanel } from "@/components/organisms/organization/organization-members-panel";
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
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDeleteOrganization,
  useOrganization,
} from "@/lib/hooks/use-organization";
import { useOrganizationMembers } from "@/lib/hooks/use-organization-members";
import { useAuth } from "@/lib/hooks/use-auth";

const ORG_SETTINGS_TABS = ["General", "Members", "API Keys"] as const;
type OrgSettingsTab = (typeof ORG_SETTINGS_TABS)[number];

type OrganizationSettingsProps = {
  organizationId: string;
};

export function OrganizationSettings({ organizationId }: OrganizationSettingsProps) {
  const t = useTranslations("organizations.settings");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { data, isLoading, error } = useOrganization(organizationId);
  const { data: members, isLoading: isMembersLoading } = useOrganizationMembers(organizationId);
  const deleteOrganization = useDeleteOrganization(organizationId);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const tabFromUrl = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<OrgSettingsTab>(
    ORG_SETTINGS_TABS.find((t) => t === tabFromUrl) ?? "General",
  );

  function handleTabChange(tab: OrgSettingsTab) {
    setActiveTab(tab);
    const next = new URLSearchParams(searchParams.toString());
    next.set("tab", tab);
    router.replace(`?${next.toString()}`, { scroll: false });
  }
  const tabLabels: Record<OrgSettingsTab, string> = {
    General: t("tabGeneral"),
    Members: t("tabMembers"),
    "API Keys": t("tabApiKeys"),
  };

  if (isLoading || isMembersLoading) {
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

  const currentMember = members?.find((m) => m.user_id === user?.id);
  if (currentMember?.role !== "owner") {
    router.replace("/organizations");
    return null;
  }

  return (
    <div className="space-y-6">
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
              onClick={() => handleTabChange(tab)}
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
    </div>
  );
}
