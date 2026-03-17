// @vitest-environment node
import { describe, expect, it } from "vitest";
import { buildUpstreamUrl } from "@/lib/proxy/url";

describe("buildUpstreamUrl", () => {
  it("should concatenate backendUrl and a single path segment", () => {
    const result = buildUpstreamUrl(
      "http://backend:8000",
      ["projects"],
      new URLSearchParams(),
    );
    expect(result).toBe("http://backend:8000/api/v1/projects");
  });

  it("should concatenate backendUrl and multiple path segments", () => {
    const result = buildUpstreamUrl(
      "http://backend:8000",
      ["projects", "42", "chat"],
      new URLSearchParams(),
    );
    expect(result).toBe("http://backend:8000/api/v1/projects/42/chat");
  });

  it("should append query string when present", () => {
    const result = buildUpstreamUrl(
      "http://backend:8000",
      ["projects"],
      new URLSearchParams("page=2&limit=10"),
    );
    expect(result).toBe("http://backend:8000/api/v1/projects?page=2&limit=10");
  });

  it("should not append '?' when query string is empty", () => {
    const result = buildUpstreamUrl(
      "http://backend:8000",
      ["projects"],
      new URLSearchParams(""),
    );
    expect(result).toBe("http://backend:8000/api/v1/projects");
  });

  it("should not double slashes when backendUrl ends with '/'", () => {
    const result = buildUpstreamUrl(
      "http://backend:8000/",
      ["projects"],
      new URLSearchParams(),
    );
    expect(result).toBe("http://backend:8000/api/v1/projects");
  });
});
