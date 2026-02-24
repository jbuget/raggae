"use client";

import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAcceptUserOrganizationInvitation,
  useUserPendingOrganizationInvitations,
} from "@/lib/hooks/use-user-invitations";

export function UserInvitationsList() {
  const { data, isLoading, error } = useUserPendingOrganizationInvitations();
  const acceptInvitation = useAcceptUserOrganizationInvitation();

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (error) {
    return <div className="text-destructive">Failed to load invitations</div>;
  }

  if (!data || data.length === 0) {
    return <p className="text-sm text-muted-foreground">No pending invitations.</p>;
  }

  return (
    <div className="space-y-3">
      {data.map((invitation) => (
        <div
          key={invitation.id}
          className="flex flex-wrap items-center justify-between gap-3 rounded-md border p-4"
        >
          <div className="space-y-1">
            <p className="text-base font-semibold">{invitation.organization_name}</p>
            <p className="text-sm text-muted-foreground">
              Role: {invitation.role}
            </p>
            <p className="text-xs text-muted-foreground">
              Expires: {new Date(invitation.expires_at).toLocaleString()}
            </p>
          </div>
          <Button
            onClick={() =>
              acceptInvitation.mutate(invitation.id, {
                onSuccess: () => toast.success("Invitation accepted"),
                onError: () => toast.error("Failed to accept invitation"),
              })
            }
            disabled={acceptInvitation.isPending}
          >
            {acceptInvitation.isPending ? "Accepting..." : "Accept"}
          </Button>
        </div>
      ))}
    </div>
  );
}
