import type { DocumentResponse } from "@/lib/types/api";
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

export function uploadDocument(
  token: string,
  projectId: string,
  file: File,
): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<DocumentResponse>(
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
