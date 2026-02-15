import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  createProject,
  deleteProject,
  getProject,
  listProjects,
  updateProject,
} from "@/lib/api/projects";
import { server } from "../../../helpers/msw-server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const mockProject = {
  id: "proj-1",
  user_id: "user-1",
  name: "Test Project",
  description: "A test project",
  system_prompt: "",
  is_published: false,
  created_at: "2026-01-01T00:00:00Z",
};

describe("listProjects", () => {
  it("should return a list of projects", async () => {
    server.use(
      http.get("/api/v1/projects", () => {
        return HttpResponse.json([mockProject]);
      }),
    );

    const result = await listProjects("token");
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe("Test Project");
  });
});

describe("getProject", () => {
  it("should return a single project", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => {
        return HttpResponse.json(mockProject);
      }),
    );

    const result = await getProject("token", "proj-1");
    expect(result.id).toBe("proj-1");
  });
});

describe("createProject", () => {
  it("should create and return a project", async () => {
    server.use(
      http.post("/api/v1/projects", async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(
          { ...mockProject, name: body.name },
          { status: 201 },
        );
      }),
    );

    const result = await createProject("token", { name: "New Project" });
    expect(result.name).toBe("New Project");
  });
});

describe("updateProject", () => {
  it("should update and return a project", async () => {
    server.use(
      http.patch("/api/v1/projects/proj-1", async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ ...mockProject, name: body.name });
      }),
    );

    const result = await updateProject("token", "proj-1", {
      name: "Updated",
    });
    expect(result.name).toBe("Updated");
  });
});

describe("deleteProject", () => {
  it("should delete a project", async () => {
    server.use(
      http.delete("/api/v1/projects/proj-1", () => {
        return new HttpResponse(null, { status: 204 });
      }),
    );

    const result = await deleteProject("token", "proj-1");
    expect(result).toBeUndefined();
  });
});
