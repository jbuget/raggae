import React from "react";
import { renderHook } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { useSidebarData } from "@/components/organisms/sidebar/use-sidebar-data";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "token", user: { id: "user-1" } }),
}));

vi.mock("@/lib/hooks/use-accessible-projects", () => ({
  useAccessibleProjects: () => ({
    personalProjects: [
      { id: "p1", name: "Personal Project", organization_id: null },
    ],
    organizationSections: [
      {
        organization: { id: "org-2", name: "Zebra Corp" },
        projects: [],
        canEdit: false,
      },
      {
        organization: { id: "org-1", name: "Alpha Corp" },
        projects: [{ id: "p2", name: "Org Project", organization_id: "org-1" }],
        canEdit: true,
      },
    ],
    editableOrganizationIds: new Set(["org-1"]),
    isLoading: false,
    error: null,
  }),
}));

vi.mock("@/lib/api/chat", () => ({
  listConversations: vi.fn().mockResolvedValue([]),
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("useSidebarData", () => {
  it("should return personal projects", () => {
    const { result } = renderHook(() => useSidebarData(), { wrapper });
    expect(result.current.personalProjects).toHaveLength(1);
    expect(result.current.personalProjects[0].id).toBe("p1");
  });

  it("should expose organizations from sections in their original order", () => {
    const { result } = renderHook(() => useSidebarData(), { wrapper });
    expect(result.current.sortedOrganizations).toHaveLength(2);
    expect(result.current.sortedOrganizations[0].name).toBe("Zebra Corp");
    expect(result.current.sortedOrganizations[1].name).toBe("Alpha Corp");
  });

  it("should include org in editableOrganizationIds when canEdit is true", () => {
    const { result } = renderHook(() => useSidebarData(), { wrapper });
    expect(result.current.editableOrganizationIds.has("org-1")).toBe(true);
    expect(result.current.editableOrganizationIds.has("org-2")).toBe(false);
  });

  it("should pass through isLoadingProjects", () => {
    const { result } = renderHook(() => useSidebarData(), { wrapper });
    expect(result.current.isLoadingProjects).toBe(false);
  });

  it("should return allProjects merging personal and org projects", () => {
    const { result } = renderHook(() => useSidebarData(), { wrapper });
    expect(result.current.allProjects).toHaveLength(2);
    expect(result.current.allProjects.map((p) => p.id)).toEqual(["p1", "p2"]);
  });
});
