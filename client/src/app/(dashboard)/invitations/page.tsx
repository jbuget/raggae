import { UserInvitationsList } from "@/components/organizations/user-invitations-list";

export default function InvitationsPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">Invitations</h1>
      <p className="text-sm text-muted-foreground">
        Accept pending invitations to join organizations.
      </p>
      <UserInvitationsList />
    </div>
  );
}
