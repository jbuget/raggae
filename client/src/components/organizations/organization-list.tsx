"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateOrganization, useOrganizations } from "@/lib/hooks/use-organizations";

export function OrganizationList() {
  const { data, isLoading, error } = useOrganizations();
  const createOrganization = useCreateOrganization();
  const [name, setName] = useState("");

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
      <div className="flex items-center gap-3">
        <Input
          placeholder="New organization name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="max-w-sm"
        />
        <Button
          onClick={() => {
            if (!name.trim()) return;
            createOrganization.mutate(
              { name: name.trim(), description: null, logo_url: null },
              {
                onSuccess: () => {
                  setName("");
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
      </div>

      {data && data.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-2">
          {data.map((organization) => (
            <div key={organization.id} className="rounded-md border p-4">
              <p className="text-base font-semibold">{organization.name}</p>
              <p className="text-sm text-muted-foreground">
                {organization.description ?? "No description"}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No organizations yet.</p>
      )}
    </div>
  );
}
