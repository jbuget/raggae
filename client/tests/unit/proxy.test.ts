// @vitest-environment node
import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { config, proxy } from "@/proxy";

const mockGetToken = vi.fn();

vi.mock("next-auth/jwt", () => ({
  getToken: (...args: unknown[]) => mockGetToken(...args),
}));

describe("proxy", () => {
  beforeEach(() => {
    mockGetToken.mockReset();
  });

  it("should redirect invitation acceptance to login with the full callback URL", async () => {
    mockGetToken.mockResolvedValue(null);
    const request = new NextRequest("http://localhost:3000/invitations/accept?token=abc");

    const response = await proxy(request);
    const location = response.headers.get("location");

    expect(response.status).toBe(307);
    expect(location).not.toBeNull();
    expect(new URL(location!).pathname).toBe("/login");
    expect(new URL(location!).searchParams.get("callbackUrl")).toBe(
      "/invitations/accept?token=abc",
    );
  });

  it("should run on invitation routes", () => {
    expect(config.matcher).toContain("/invitations/:path*");
  });
});
