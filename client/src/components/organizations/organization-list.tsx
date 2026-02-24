"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
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
import { useCreateOrganization, useOrganizations } from "@/lib/hooks/use-organizations";

export function OrganizationList() {
  const { data, isLoading, error } = useOrganizations();
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
          <Button>Create organization</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create organization</DialogTitle>
            <DialogDescription>
              Set a name, URL slug, and optional description.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <Input
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Input
              placeholder="Slug (e.g. acme)"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
            <Textarea
              placeholder="Description (optional)"
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
                      toast.success("Organization created");
                    },
                    onError: () => toast.error("Failed to create organization"),
                  },
                );
              }}
              disabled={createOrganization.isPending}
            >
              {createOrganization.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {data && data.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-2">
          {data.map((organization) => (
            <div key={organization.id} className="rounded-md border p-4">
              <p className="text-base font-semibold">{organization.name}</p>
              <p className="text-xs text-muted-foreground">
                {organization.slug ? `/${organization.slug}` : "No slug"}
              </p>
              <p className="text-sm text-muted-foreground">
                {organization.description ?? "No description"}
              </p>
              <Button asChild variant="outline" size="sm" className="mt-3">
                <Link href={`/organizations/${organization.id}`}>Manage</Link>
              </Button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No organizations yet.</p>
      )}
    </div>
  );
}
