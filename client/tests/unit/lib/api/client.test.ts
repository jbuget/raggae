import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { ApiError, apiFetch } from "@/lib/api/client";
import { server } from "../../../helpers/msw-server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("apiFetch", () => {
  it("should make a GET request and return JSON", async () => {
    server.use(
      http.get("/api/v1/test", () => {
        return HttpResponse.json({ message: "ok" });
      }),
    );

    const result = await apiFetch<{ message: string }>("/test");
    expect(result).toEqual({ message: "ok" });
  });

  it("should include Authorization header when token is provided", async () => {
    server.use(
      http.get("/api/v1/protected", ({ request }) => {
        const auth = request.headers.get("Authorization");
        return HttpResponse.json({ auth });
      }),
    );

    const result = await apiFetch<{ auth: string }>("/protected", {
      token: "my-token",
    });
    expect(result.auth).toBe("Bearer my-token");
  });

  it("should throw ApiError on 401", async () => {
    server.use(
      http.get("/api/v1/unauthorized", () => {
        return HttpResponse.json(
          { detail: "Missing access token" },
          { status: 401 },
        );
      }),
    );

    await expect(apiFetch("/unauthorized")).rejects.toThrow(ApiError);
    await expect(apiFetch("/unauthorized")).rejects.toMatchObject({
      status: 401,
      message: "Missing access token",
    });
  });

  it("should return undefined for 204 responses", async () => {
    server.use(
      http.delete("/api/v1/resource", () => {
        return new HttpResponse(null, { status: 204 });
      }),
    );

    const result = await apiFetch("/resource", { method: "DELETE" });
    expect(result).toBeUndefined();
  });

  it("should set Content-Type for JSON body", async () => {
    server.use(
      http.post("/api/v1/data", async ({ request }) => {
        const contentType = request.headers.get("Content-Type");
        const body = await request.json();
        return HttpResponse.json({ contentType, body });
      }),
    );

    const result = await apiFetch<{ contentType: string; body: unknown }>(
      "/data",
      {
        method: "POST",
        body: JSON.stringify({ name: "test" }),
      },
    );
    expect(result.contentType).toBe("application/json");
    expect(result.body).toEqual({ name: "test" });
  });
});
