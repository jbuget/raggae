import type {
  DocumentChunksResponse,
  DocumentResponse,
  UploadDocumentsResponse,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function listDocuments(
  token: string,
  projectId: string,
): Promise<DocumentResponse[]> {
  return apiFetch<DocumentResponse[]>(
    `/projects/${projectId}/documents`,
    { token },
  );
}

export function uploadDocuments(
  token: string,
  projectId: string,
  files: File[],
  onProgress?: (percent: number) => void,
): Promise<UploadDocumentsResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }

    const xhr = new XMLHttpRequest();

    if (onProgress) {
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          // Cap at 95 — the remaining 5% represents server-side processing
          onProgress(Math.min(95, Math.round((e.loaded / e.total) * 100)));
        }
      });
    }

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText) as UploadDocumentsResponse);
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });
    xhr.addEventListener("error", () => reject(new Error("Upload failed")));

    xhr.open("POST", `/api/v1/projects/${projectId}/documents`);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.send(formData);
  });
}

export function deleteDocument(
  token: string,
  projectId: string,
  documentId: string,
): Promise<void> {
  return apiFetch<void>(
    `/projects/${projectId}/documents/${documentId}`,
    { method: "DELETE", token },
  );
}

export function reindexDocument(
  token: string,
  projectId: string,
  documentId: string,
): Promise<DocumentResponse> {
  return apiFetch<DocumentResponse>(
    `/projects/${projectId}/documents/${documentId}/reindex`,
    { method: "POST", token },
  );
}

export function getDocumentChunks(
  token: string,
  projectId: string,
  documentId: string,
): Promise<DocumentChunksResponse> {
  return apiFetch<DocumentChunksResponse>(
    `/projects/${projectId}/documents/${documentId}/chunks`,
    { token },
  );
}

export async function getDocumentFileBlob(
  token: string,
  projectId: string,
  documentId: string,
): Promise<Blob> {
  const response = await fetch(
    `/api/v1/projects/${projectId}/documents/${documentId}/file`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Unable to fetch document file (${response.status})`);
  }

  return response.blob();
}
