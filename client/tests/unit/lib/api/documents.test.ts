import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import {
  deleteDocument,
  listDocuments,
  uploadDocuments,
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

describe("uploadDocuments", () => {
  it("should upload files and return detailed batch result", async () => {
    server.use(
      http.post("/api/v1/projects/proj-1/documents", () => {
        return HttpResponse.json(
          {
            total: 2,
            succeeded: 1,
            failed: 1,
            created: [
              {
                original_filename: "test.pdf",
                stored_filename: "test.pdf",
                document_id: "doc-1",
              },
            ],
            errors: [
              {
                filename: "bad.exe",
                code: "INVALID_FILE_TYPE",
                message: "Unsupported document type: exe",
              },
            ],
          },
          { status: 200 },
        );
      }),
    );

    const fileOne = new File(["content"], "test.pdf", {
      type: "application/pdf",
    });
    const fileTwo = new File(["content"], "bad.exe", {
      type: "application/octet-stream",
    });
    const result = await uploadDocuments("token", "proj-1", [fileOne, fileTwo]);
    expect(result.succeeded).toBe(1);
    expect(result.failed).toBe(1);
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
