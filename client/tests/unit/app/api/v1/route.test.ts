// @vitest-environment node
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { NextRequest } from "next/server";
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { GET, POST, DELETE, PATCH } from "@/app/api/v1/[...path]/route";

const BACKEND_URL = "http://fake-backend:8000";

vi.stubEnv("BACKEND_URL", BACKEND_URL);

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("GET /api/v1/[...path]", () => {
  it("should proxy to the backend and return JSON", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects`, () =>
        HttpResponse.json([{ id: 1, name: "Projet A" }]),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects");
    const res = await GET(req, { params: Promise.resolve({ path: ["projects"] }) });

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual([{ id: 1, name: "Projet A" }]);
  });

  it("should forward query string to the backend", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects`, ({ request }) => {
        const url = new URL(request.url);
        return HttpResponse.json({ page: url.searchParams.get("page") });
      }),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects?page=2");
    const res = await GET(req, { params: Promise.resolve({ path: ["projects"] }) });

    const body = await res.json();
    expect(body.page).toBe("2");
  });

  it("should forward Authorization header to the backend", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects`, ({ request }) =>
        HttpResponse.json({ auth: request.headers.get("authorization") }),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects", {
      headers: { Authorization: "Bearer my-token" },
    });
    const res = await GET(req, { params: Promise.resolve({ path: ["projects"] }) });

    const body = await res.json();
    expect(body.auth).toBe("Bearer my-token");
  });

  it("should preserve the backend status code", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects/999`, () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 }),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects/999");
    const res = await GET(req, { params: Promise.resolve({ path: ["projects", "999"] }) });

    expect(res.status).toBe(404);
  });

  it("should preserve Content-Type from the backend response", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects`, () =>
        HttpResponse.json([], { headers: { "Content-Type": "application/json; charset=utf-8" } }),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects");
    const res = await GET(req, { params: Promise.resolve({ path: ["projects"] }) });

    expect(res.headers.get("content-type")).toContain("application/json");
  });

  it("should return 502 when the backend is unreachable", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/projects`, () => HttpResponse.error()),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects");
    const res = await GET(req, { params: Promise.resolve({ path: ["projects"] }) });

    expect(res.status).toBe(502);
  });

  it("should return a streaming body (ReadableStream, not buffered)", async () => {
    server.use(
      http.get(`${BACKEND_URL}/api/v1/stream`, () =>
        HttpResponse.json({ streamed: true }),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/stream");
    const res = await GET(req, { params: Promise.resolve({ path: ["stream"] }) });

    expect(res.body).toBeInstanceOf(ReadableStream);
  });
});

describe("POST /api/v1/[...path]", () => {
  it("should forward JSON body to the backend", async () => {
    server.use(
      http.post(`${BACKEND_URL}/api/v1/projects`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json(body, { status: 201 });
      }),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Nouveau projet" }),
    });
    const res = await POST(req, { params: Promise.resolve({ path: ["projects"] }) });

    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body).toEqual({ name: "Nouveau projet" });
  });
});

describe("DELETE /api/v1/[...path]", () => {
  it("should proxy DELETE and return 204", async () => {
    server.use(
      http.delete(`${BACKEND_URL}/api/v1/projects/1`, () =>
        new HttpResponse(null, { status: 204 }),
      ),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects/1", {
      method: "DELETE",
    });
    const res = await DELETE(req, { params: Promise.resolve({ path: ["projects", "1"] }) });

    expect(res.status).toBe(204);
  });
});

describe("PATCH /api/v1/[...path]", () => {
  it("should forward PATCH body to the backend", async () => {
    server.use(
      http.patch(`${BACKEND_URL}/api/v1/projects/1`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({ ...body, id: 1 });
      }),
    );

    const req = new NextRequest("http://localhost:3000/api/v1/projects/1", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Modifié" }),
    });
    const res = await PATCH(req, { params: Promise.resolve({ path: ["projects", "1"] }) });

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual({ id: 1, name: "Modifié" });
  });
});
