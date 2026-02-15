import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "@/lib/api/documents";
import { server } from "../../../helpers/msw-server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const mockDoc = {
  id: "doc-1",
  project_id: "proj-1",
  file_name: "test.pdf",
  content_type: "application/pdf",
  file_size: 1024,
  created_at: "2026-01-01T00:00:00Z",
  processing_strategy: null,
};

describe("listDocuments", () => {
  it("should return documents for a project", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents", () => {
        return HttpResponse.json([mockDoc]);
      }),
    );

    const result = await listDocuments("token", "proj-1");
    expect(result).toHaveLength(1);
    expect(result[0].file_name).toBe("test.pdf");
  });
});

describe("uploadDocument", () => {
  it("should upload a file and return document", async () => {
    server.use(
      http.post("/api/v1/projects/proj-1/documents", () => {
        return HttpResponse.json(mockDoc, { status: 201 });
      }),
    );

    const file = new File(["content"], "test.pdf", {
      type: "application/pdf",
    });
    const result = await uploadDocument("token", "proj-1", file);
    expect(result.file_name).toBe("test.pdf");
  });
});

describe("deleteDocument", () => {
  it("should delete a document", async () => {
    server.use(
      http.delete("/api/v1/projects/proj-1/documents/doc-1", () => {
        return new HttpResponse(null, { status: 204 });
      }),
    );

    const result = await deleteDocument("token", "proj-1", "doc-1");
    expect(result).toBeUndefined();
  });
});
