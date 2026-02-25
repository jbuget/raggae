"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import type { OrganizationMemberRole } from "@/lib/types/api";
import {
  useInviteOrganizationMember,
  useOrganizationInvitations,
  useOrganizationMembers,
  useRemoveOrganizationMember,
  useResendOrganizationInvitation,
  useRevokeOrganizationInvitation,
  useUpdateOrganizationMemberRole,
} from "@/lib/hooks/use-organization-members";

const ROLE_OPTIONS: OrganizationMemberRole[] = ["owner", "maker", "user"];

type OrganizationMembersPanelProps = {
  organizationId: string;
};

export function OrganizationMembersPanel({ organizationId }: OrganizationMembersPanelProps) {
  const { data: members, isLoading: membersLoading } = useOrganizationMembers(organizationId);
  const { data: invitations, isLoading: invitationsLoading } =
    useOrganizationInvitations(organizationId);
  const inviteMember = useInviteOrganizationMember(organizationId);
  const updateRole = useUpdateOrganizationMemberRole(organizationId);
  const removeMember = useRemoveOrganizationMember(organizationId);
  const resendInvitation = useResendOrganizationInvitation(organizationId);
  const revokeInvitation = useRevokeOrganizationInvitation(organizationId);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<OrganizationMemberRole>("user");

  return (
    <div className="rounded-lg border p-5 space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Members</h2>
        <p className="text-sm text-muted-foreground">
          Invite, change roles, and remove members from this organization.
        </p>
      </div>

      <div className="space-y-3">
        <Label>Invite member</Label>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            placeholder="user@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="max-w-sm"
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as OrganizationMemberRole)}
            className="h-9 rounded-md border bg-background px-3 text-sm"
          >
            {ROLE_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <Button
            onClick={() =>
              inviteMember.mutate(
                { email: email.trim(), role },
                {
                  onSuccess: () => {
                    setEmail("");
                    setRole("user");
                    toast.success("Invitation sent");
                  },
                  onError: () => toast.error("Failed to invite member"),
                },
              )
            }
            disabled={!email.trim() || inviteMember.isPending}
          >
            {inviteMember.isPending ? "Sending..." : "Invite"}
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Current members</Label>
        {membersLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <div className="space-y-2">
            {members?.map((member) => (
              <div
                key={member.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
              >
                <div className="text-sm">
                  <p className="font-medium">
                    {[member.user_first_name, member.user_last_name]
                      .filter(Boolean)
                      .join(" ") || member.user_id}
                  </p>
                  <p className="text-muted-foreground">Joined {member.joined_at}</p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={member.role}
                    onChange={(e) =>
                      updateRole.mutate(
                        {
                          memberId: member.id,
                          role: e.target.value as OrganizationMemberRole,
                        },
                        {
                          onError: () => toast.error("Failed to update role"),
                        },
                      )
                    }
                    className="h-9 rounded-md border bg-background px-3 text-sm"
                    disabled={updateRole.isPending}
                  >
                    {ROLE_OPTIONS.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                  <Button
                    variant="outline"
                    onClick={() =>
                      removeMember.mutate(member.id, {
                        onSuccess: () => toast.success("Member removed"),
                        onError: () => toast.error("Failed to remove member"),
                      })
                    }
                    disabled={removeMember.isPending}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label>Pending invitations</Label>
        {invitationsLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <div className="space-y-2">
            {!invitations || invitations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No pending invitations.</p>
            ) : (
              invitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
                >
                  <div className="text-sm">
                    <p className="font-medium">{invitation.email}</p>
                    <p className="text-muted-foreground">
                      {invitation.role} - {invitation.status}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() =>
                        resendInvitation.mutate(invitation.id, {
                          onSuccess: () => toast.success("Invitation resent"),
                          onError: () => toast.error("Failed to resend invitation"),
                        })
                      }
                      disabled={resendInvitation.isPending}
                    >
                      Resend
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() =>
                        revokeInvitation.mutate(invitation.id, {
                          onSuccess: () => toast.success("Invitation revoked"),
                          onError: () => toast.error("Failed to revoke invitation"),
                        })
                      }
                      disabled={revokeInvitation.isPending}
                    >
                      Revoke
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
