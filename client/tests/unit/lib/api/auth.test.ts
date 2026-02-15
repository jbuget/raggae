import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { login, register } from "@/lib/api/auth";
import { server } from "../../../helpers/msw-server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("register", () => {
  it("should register a new user", async () => {
    server.use(
      http.post("/api/v1/auth/register", async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(
          {
            id: "user-1",
            email: body.email,
            full_name: body.full_name,
            is_active: true,
            created_at: "2026-01-01T00:00:00Z",
          },
          { status: 201 },
        );
      }),
    );

    const result = await register({
      email: "test@example.com",
      password: "password123",
      full_name: "Test User",
    });

    expect(result.email).toBe("test@example.com");
    expect(result.full_name).toBe("Test User");
  });
});

describe("login", () => {
  it("should return a token", async () => {
    server.use(
      http.post("/api/v1/auth/login", () => {
        return HttpResponse.json({
          access_token: "jwt-token",
          token_type: "bearer",
        });
      }),
    );

    const result = await login({
      email: "test@example.com",
      password: "password123",
    });

    expect(result.access_token).toBe("jwt-token");
    expect(result.token_type).toBe("bearer");
  });
});
