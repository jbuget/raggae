"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { OrganizationMembersPanel } from "@/components/organizations/organization-members-panel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  useDeleteOrganization,
  useOrganization,
  useUpdateOrganization,
} from "@/lib/hooks/use-organization";

type OrganizationSettingsProps = {
  organizationId: string;
};

export function OrganizationSettings({ organizationId }: OrganizationSettingsProps) {
  const router = useRouter();
  const { data, isLoading, error } = useOrganization(organizationId);
  const deleteOrganization = useDeleteOrganization(organizationId);

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-96" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-destructive">Failed to load organization.</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Organization settings</h1>
        <p className="text-sm text-muted-foreground">Manage organization profile and access.</p>
      </div>

      <OrganizationProfileForm
        key={`${data.id}-${data.updated_at}`}
        organizationId={organizationId}
        initialName={data.name}
        initialSlug={data.slug}
        initialDescription={data.description}
        initialLogoUrl={data.logo_url}
      />

      <div className="rounded-lg border border-destructive/40 p-5 space-y-3">
        <p className="text-sm font-medium text-destructive">Danger zone</p>
        <p className="text-sm text-muted-foreground">
          Delete this organization and all related data.
        </p>
        <Button
          variant="destructive"
          onClick={() =>
            deleteOrganization.mutate(undefined, {
              onSuccess: () => {
                toast.success("Organization deleted");
                router.push("/organizations");
              },
              onError: () => toast.error("Failed to delete organization"),
            })
          }
          disabled={deleteOrganization.isPending}
        >
          {deleteOrganization.isPending ? "Deleting..." : "Delete organization"}
        </Button>
      </div>

      <OrganizationMembersPanel organizationId={organizationId} />
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
  const updateOrganization = useUpdateOrganization(organizationId);
  const [name, setName] = useState(initialName);
  const [slug, setSlug] = useState(initialSlug ?? "");
  const [description, setDescription] = useState(initialDescription ?? "");
  const [logoUrl, setLogoUrl] = useState(initialLogoUrl ?? "");

  return (
    <div className="rounded-lg border p-5 space-y-4">
      <div className="space-y-2">
        <Label htmlFor="org-name">Name</Label>
        <Input id="org-name" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-slug">Slug</Label>
        <Input id="org-slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-description">Description</Label>
        <Textarea
          id="org-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-logo-url">Logo URL</Label>
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
              onSuccess: () => toast.success("Organization updated"),
              onError: () => toast.error("Failed to update organization"),
            },
          )
        }
        disabled={updateOrganization.isPending || !name.trim()}
      >
        {updateOrganization.isPending ? "Saving..." : "Save"}
      </Button>
    </div>
  );
}
