import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { useQueries } from "@tanstack/react-query";
import { useSidebarData } from "@/components/organisms/sidebar/use-sidebar-data";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "token", user: { id: "user-1" } }),
}));

vi.mock("@/lib/hooks/use-projects", () => ({
  useProjects: () => ({
    data: [
      { id: "p1", name: "Personal Project", organization_id: null },
      { id: "p2", name: "Org Project", organization_id: "org-1" },
    ],
    isLoading: false,
  }),
}));

vi.mock("@/lib/hooks/use-organizations", () => ({
  useOrganizations: () => ({
    data: [
      { id: "org-2", name: "Zebra Corp" },
      { id: "org-1", name: "Alpha Corp" },
    ],
  }),
}));

vi.mock("@tanstack/react-query", async (importOriginal) => {
  const mod = (await importOriginal()) as Record<string, unknown>;
  return { ...mod, useQueries: vi.fn() };
});

describe("useSidebarData", () => {
  beforeEach(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (useQueries as any).mockImplementation(({ queries }: { queries: Array<{ queryKey: string[] }> }) => {
      if (!queries.length) return [];
      const firstKey = queries[0].queryKey[0];
      if (firstKey === "organization-projects") {
        return queries.map(() => ({ data: [] }));
      }
      return [
        { data: [{ user_id: "user-1", role: "owner" }] },
        { data: [] },
      ];
    });
  });

  it("should return only personal projects (no organization_id)", () => {
    const { result } = renderHook(() => useSidebarData());
    expect(result.current.personalProjects).toHaveLength(1);
    expect(result.current.personalProjects[0].id).toBe("p1");
  });

  it("should sort organizations alphabetically", () => {
    const { result } = renderHook(() => useSidebarData());
    expect(result.current.sortedOrganizations[0].name).toBe("Alpha Corp");
    expect(result.current.sortedOrganizations[1].name).toBe("Zebra Corp");
  });

  it("should include org in editableOrganizationIds when user is owner", () => {
    const { result } = renderHook(() => useSidebarData());
    expect(result.current.editableOrganizationIds.has("org-1")).toBe(true);
    expect(result.current.editableOrganizationIds.has("org-2")).toBe(false);
  });

  it("should pass through isLoadingProjects", () => {
    const { result } = renderHook(() => useSidebarData());
    expect(result.current.isLoadingProjects).toBe(false);
  });
});
