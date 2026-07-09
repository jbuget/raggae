import type { QueryClient } from "@tanstack/react-query";

export function refreshAcceptedOrganizationInvitationQueries(
  queryClient: QueryClient,
): Promise<void> {
  return Promise.all([
    queryClient.invalidateQueries({
      queryKey: ["organizations"],
      refetchType: "all",
    }),
    queryClient.invalidateQueries({
      queryKey: ["accessible-projects"],
      refetchType: "all",
    }),
    queryClient.invalidateQueries({
      queryKey: ["user-pending-organization-invitations"],
      refetchType: "all",
    }),
  ]).then(() => undefined);
}
