import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import {
  deleteDocument,
  listDocuments,
  uploadDocuments,
} from "@/lib/api/documents";
import { server } from "../../../helpers/msw-server";

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

function makeXhrMock(status: number, responseText: string, progress?: { loaded: number; total: number }) {
  const handlers: Record<string, (e: Event) => void> = {};
  const uploadHandlers: Record<string, (e: ProgressEvent) => void> = {};
  const mock = {
    status,
    responseText,
    upload: {
      addEventListener: vi.fn((ev: string, fn: (e: ProgressEvent) => void) => {
        uploadHandlers[ev] = fn;
      }),
    },
    addEventListener: vi.fn((ev: string, fn: (e: Event) => void) => {
      handlers[ev] = fn;
    }),
    open: vi.fn(),
    setRequestHeader: vi.fn(),
    send: vi.fn(() => {
      if (progress) {
        uploadHandlers["progress"]?.(
          new ProgressEvent("progress", { loaded: progress.loaded, total: progress.total, lengthComputable: true }),
        );
      }
      setTimeout(() => handlers["load"]?.(new Event("load")), 0);
    }),
  };
  // Regular function required — arrow functions cannot be used as constructors with `new`
  vi.stubGlobal("XMLHttpRequest", vi.fn(function () { return mock; }));
  return mock;
}

describe("uploadDocuments", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("should upload files and return detailed batch result", async () => {
    const xhrMock = makeXhrMock(
      200,
      JSON.stringify({
        total: 2,
        succeeded: 1,
        failed: 1,
        created: [{ original_filename: "test.pdf", stored_filename: "test.pdf", document_id: "doc-1" }],
        errors: [{ filename: "bad.exe", code: "INVALID_FILE_TYPE", message: "Unsupported document type: exe" }],
      }),
    );

    const fileOne = new File(["content"], "test.pdf", { type: "application/pdf" });
    const fileTwo = new File(["content"], "bad.exe", { type: "application/octet-stream" });
    const result = await uploadDocuments("token", "proj-1", [fileOne, fileTwo]);

    expect(result.succeeded).toBe(1);
    expect(result.failed).toBe(1);
    expect(xhrMock.open).toHaveBeenCalledWith("POST", "/api/v1/projects/proj-1/documents");
    expect(xhrMock.setRequestHeader).toHaveBeenCalledWith("Authorization", "Bearer token");
  });

  it("should report upload progress via onProgress callback", async () => {
    makeXhrMock(200, JSON.stringify({ total: 0, succeeded: 0, failed: 0, created: [], errors: [] }), {
      loaded: 50,
      total: 100,
    });

    const onProgress = vi.fn();
    await uploadDocuments("token", "proj-1", [], onProgress);

    expect(onProgress).toHaveBeenCalledWith(50);
  });

  it("should reject with ApiError on HTTP error", async () => {
    makeXhrMock(422, JSON.stringify({ detail: "Invalid token" }));

    const { ApiError } = await import("@/lib/api/client");
    await expect(uploadDocuments("token", "proj-1", [])).rejects.toBeInstanceOf(ApiError);
    await expect(uploadDocuments("token", "proj-1", [])).rejects.toMatchObject({ status: 422 });
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
