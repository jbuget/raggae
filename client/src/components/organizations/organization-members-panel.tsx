"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/client";
import { Badge } from "@/components/ui/badge";
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
  const t = useTranslations("organizations.members");
  const tCommon = useTranslations("common");
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
        <h2 className="text-lg font-semibold">{t("title")}</h2>
        <p className="text-sm text-muted-foreground">
          {t("description")}
        </p>
      </div>

      <div className="space-y-3">
        <Label>{t("inviteLabel")}</Label>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            placeholder={t("invitePlaceholder")}
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
                    toast.success(t("inviteSuccess"));
                  },
                  onError: (err) => {
                    if (err instanceof ApiError && err.status === 409) {
                      toast.error(t("inviteAlreadyPending"));
                    } else {
                      toast.error(t("inviteError"));
                    }
                  },
                },
              )
            }
            disabled={!email.trim() || inviteMember.isPending}
          >
            {inviteMember.isPending ? tCommon("sending") : t("inviteLabel")}
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <Label>{t("currentMembers")}</Label>
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
                  <div className="flex items-baseline gap-2">
                    <p className="font-medium">
                      {[member.user_first_name, member.user_last_name]
                        .filter(Boolean)
                        .join(" ") || member.user_id}
                    </p>
                    {member.user_email && (
                      <p className="text-muted-foreground">{member.user_email}</p>
                    )}
                  </div>
                  <p className="text-muted-foreground">{t("joined")} {member.joined_at}</p>
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
                        onError: () => toast.error(t("removeError")),
                      })
                    }
                    disabled={removeMember.isPending}
                  >
                    {t("remove")}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label>{t("pendingInvitations")}</Label>
        {invitationsLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <div className="space-y-2">
            {!invitations || invitations.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("noPendingInvitations")}</p>
            ) : (
              invitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
                >
                  <div className="text-sm">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{invitation.email}</p>
                      {(invitation.status === "expired" || new Date(invitation.expires_at) < new Date()) && (
                        <Badge variant="destructive">{t("expired")}</Badge>
                      )}
                    </div>
                    <p className="text-muted-foreground">
                      {t("sentOn")} {new Date(invitation.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        const url = `${window.location.origin}/invitations/accept?token=${invitation.token_hash}`;
                        navigator.clipboard.writeText(url);
                        toast.success(t("copyLinkSuccess"));
                      }}
                    >
                      {t("copyLink")}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() =>
                        resendInvitation.mutate(invitation.id, {
                          onSuccess: () => toast.success(t("resendSuccess")),
                          onError: () => toast.error(t("resendError")),
                        })
                      }
                      disabled={resendInvitation.isPending}
                    >
                      {t("resend")}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() =>
                        revokeInvitation.mutate(invitation.id, {
                          onSuccess: () => toast.success(t("revokeSuccess")),
                          onError: () => toast.error(t("revokeError")),
                        })
                      }
                      disabled={revokeInvitation.isPending}
                    >
                      {t("revoke")}
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
