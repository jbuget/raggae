"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { useQueries } from "@tanstack/react-query";
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
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { listOrganizationMembers } from "@/lib/api/organizations";
import { useAuth } from "@/lib/hooks/use-auth";
import { useCreateOrganization, useOrganizations } from "@/lib/hooks/use-organizations";

export function OrganizationList() {
  const t = useTranslations("organizations");
  const tCommon = useTranslations("common");
  const { token, user } = useAuth();
  const { data, isLoading, error } = useOrganizations();
  const sortedOrganizations = [...(data ?? [])].sort((a, b) =>
    a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
  );
  const organizationMembersQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-members", organization.id],
      queryFn: () => listOrganizationMembers(token!, organization.id),
      enabled: !!token && !!user?.id,
    })),
  });
  const ownerOrganizationIds = new Set(
    sortedOrganizations
      .filter((organization, index) => {
        const members = organizationMembersQueries[index]?.data ?? [];
        const currentUserMember = members.find((member) => member.user_id === user?.id);
        return currentUserMember?.role === "owner";
      })
      .map((organization) => organization.id),
  );
  const createOrganization = useCreateOrganization();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (error) {
    return <div className="text-destructive">Failed to load organizations</div>;
  }

  return (
    <div className="space-y-6">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button>{t("list.createTitle")}</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("list.createTitle")}</DialogTitle>
            <DialogDescription>
              {t("list.createDescription")}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <Input
              placeholder={t("list.namePlaceholder")}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Input
              placeholder={t("list.slugPlaceholder")}
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
            <Textarea
              placeholder={t("list.descriptionPlaceholder")}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button
              onClick={() => {
                if (!name.trim()) return;
                createOrganization.mutate(
                  {
                    name: name.trim(),
                    slug: slug.trim() || null,
                    description: description.trim() || null,
                    logo_url: null,
                  },
                  {
                    onSuccess: () => {
                      setOpen(false);
                      setName("");
                      setSlug("");
                      setDescription("");
                      toast.success(t("list.createSuccess"));
                    },
                    onError: () => toast.error(t("list.createError")),
                  },
                );
              }}
              disabled={createOrganization.isPending}
            >
              {createOrganization.isPending ? tCommon("creating") : tCommon("confirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {sortedOrganizations.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-2">
          {sortedOrganizations.map((organization) => (
            <div key={organization.id} className="rounded-md border p-4">
              <p className="text-base font-semibold">{organization.name}</p>
              <p className="text-xs text-muted-foreground">
                {organization.slug ? `/${organization.slug}` : t("list.noSlug")}
              </p>
              <p className="text-sm text-muted-foreground">
                {organization.description ?? tCommon("noDescription")}
              </p>
              {ownerOrganizationIds.has(organization.id) && (
                <Button asChild variant="outline" size="sm" className="mt-3">
                  <Link href={`/organizations/${organization.id}`}>{t("list.manage")}</Link>
                </Button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{t("list.empty")}</p>
      )}
    </div>
  );
}
