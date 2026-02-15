import type { DocumentResponse, UploadDocumentsResponse } from "@/lib/types/api";
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
): Promise<UploadDocumentsResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  return apiFetch<UploadDocumentsResponse>(
    `/projects/${projectId}/documents`,
    {
      method: "POST",
      body: formData,
      token,
    },
  );
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
