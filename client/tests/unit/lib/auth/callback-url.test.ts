import { describe, expect, it } from "vitest";
import { buildAuthRedirectPath, getSafeAuthCallbackUrl } from "@/lib/auth/callback-url";

describe("getSafeAuthCallbackUrl", () => {
  it("returns /projects when value is null", () => {
    expect(getSafeAuthCallbackUrl(null)).toBe("/projects");
  });

  it("returns /projects when value is empty", () => {
    expect(getSafeAuthCallbackUrl("")).toBe("/projects");
  });

  it("rejects protocol-relative URLs", () => {
    expect(getSafeAuthCallbackUrl("//evil.com")).toBe("/projects");
  });

  it("rejects absolute URLs", () => {
    expect(getSafeAuthCallbackUrl("https://evil.com")).toBe("/projects");
  });

  it("rejects values that do not start with a slash", () => {
    expect(getSafeAuthCallbackUrl("projects")).toBe("/projects");
  });

  it("accepts internal relative paths", () => {
    expect(getSafeAuthCallbackUrl("/invitations/accept?token=abc")).toBe(
      "/invitations/accept?token=abc",
    );
  });
});

describe("buildAuthRedirectPath", () => {
  it("returns the bare path when callbackUrl is null", () => {
    expect(buildAuthRedirectPath("/login", null)).toBe("/login");
  });

  it("attaches a safe callbackUrl when provided", () => {
    expect(buildAuthRedirectPath("/login", "/invitations/accept?token=abc")).toBe(
      "/login?callbackUrl=%2Finvitations%2Faccept%3Ftoken%3Dabc",
    );
  });

  it("normalizes a malicious callbackUrl to the safe fallback", () => {
    expect(buildAuthRedirectPath("/login", "//evil.com")).toBe(
      "/login?callbackUrl=%2Fprojects",
    );
  });
});
