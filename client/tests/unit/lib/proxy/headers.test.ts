// @vitest-environment node
import { describe, expect, it } from "vitest";
import { buildUpstreamHeaders, buildResponseHeaders } from "@/lib/proxy/headers";

describe("buildUpstreamHeaders", () => {
  it("should forward Authorization header", () => {
    const headers = new Headers({ Authorization: "Bearer token123" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("authorization")).toBe("Bearer token123");
  });

  it("should forward Content-Type header", () => {
    const headers = new Headers({ "Content-Type": "application/json" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("content-type")).toBe("application/json");
  });

  it("should remove 'host' header", () => {
    const headers = new Headers({ host: "localhost:3000" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("host")).toBeNull();
  });

  it("should remove 'connection' hop-by-hop header", () => {
    const headers = new Headers({ connection: "keep-alive" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("connection")).toBeNull();
  });

  it("should remove 'transfer-encoding' hop-by-hop header", () => {
    const headers = new Headers({ "transfer-encoding": "chunked" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("transfer-encoding")).toBeNull();
  });

  it("should remove 'keep-alive' hop-by-hop header", () => {
    const headers = new Headers({ "keep-alive": "timeout=5" });
    const result = buildUpstreamHeaders(headers);
    expect(result.get("keep-alive")).toBeNull();
  });

  it("should add X-Forwarded-For when clientIp is provided", () => {
    const headers = new Headers();
    const result = buildUpstreamHeaders(headers, "1.2.3.4");
    expect(result.get("x-forwarded-for")).toBe("1.2.3.4");
  });

  it("should not add X-Forwarded-For when clientIp is absent", () => {
    const headers = new Headers();
    const result = buildUpstreamHeaders(headers);
    expect(result.get("x-forwarded-for")).toBeNull();
  });
});

describe("buildResponseHeaders", () => {
  it("should forward Content-Type header", () => {
    const headers = new Headers({ "Content-Type": "application/json" });
    const result = buildResponseHeaders(headers);
    expect(result.get("content-type")).toBe("application/json");
  });

  it("should remove 'connection' hop-by-hop header", () => {
    const headers = new Headers({ connection: "keep-alive" });
    const result = buildResponseHeaders(headers);
    expect(result.get("connection")).toBeNull();
  });

  it("should remove 'transfer-encoding' hop-by-hop header", () => {
    const headers = new Headers({ "transfer-encoding": "chunked" });
    const result = buildResponseHeaders(headers);
    expect(result.get("transfer-encoding")).toBeNull();
  });

  it("should remove 'content-encoding' to avoid double-decompression", () => {
    // fetch() décompresse automatiquement la réponse.
    // Retransmettre Content-Encoding ferait croire au browser
    // que le body est encore compressé → corruption silencieuse.
    const headers = new Headers({ "content-encoding": "gzip" });
    const result = buildResponseHeaders(headers);
    expect(result.get("content-encoding")).toBeNull();
  });

  it("should forward a single Set-Cookie header", () => {
    const headers = new Headers();
    headers.append("set-cookie", "session=abc; HttpOnly");
    const result = buildResponseHeaders(headers);
    expect(result.getSetCookie()).toEqual(["session=abc; HttpOnly"]);
  });

  it("should forward multiple Set-Cookie headers without losing any", () => {
    // L'API Headers déduplique les headers de même nom si on utilise set().
    // Il faut utiliser append() ou getSetCookie() pour éviter les pertes.
    const headers = new Headers();
    headers.append("set-cookie", "session=abc; HttpOnly");
    headers.append("set-cookie", "refresh=xyz; HttpOnly");
    const result = buildResponseHeaders(headers);
    expect(result.getSetCookie()).toHaveLength(2);
    expect(result.getSetCookie()).toContain("session=abc; HttpOnly");
    expect(result.getSetCookie()).toContain("refresh=xyz; HttpOnly");
  });

  it("should not error when Set-Cookie is absent", () => {
    const headers = new Headers({ "content-type": "application/json" });
    const result = buildResponseHeaders(headers);
    expect(result.getSetCookie()).toEqual([]);
  });
});
