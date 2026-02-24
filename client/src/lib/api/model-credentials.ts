import { apiFetch } from "@/lib/api/client";
import type {
  ModelCredentialResponse,
  SaveModelCredentialRequest,
} from "@/lib/types/api";

export function listModelCredentials(token: string): Promise<ModelCredentialResponse[]> {
  return apiFetch<ModelCredentialResponse[]>("/model-credentials", { token });
}

export function createModelCredential(
  token: string,
  data: SaveModelCredentialRequest,
): Promise<ModelCredentialResponse> {
  return apiFetch<ModelCredentialResponse>("/model-credentials", {
    method: "POST",
    token,
    body: JSON.stringify(data),
  });
}

export function activateModelCredential(token: string, credentialId: string): Promise<void> {
  return apiFetch<void>(`/model-credentials/${credentialId}/activate`, {
    method: "PATCH",
    token,
  });
}

export function deactivateModelCredential(token: string, credentialId: string): Promise<void> {
  return apiFetch<void>(`/model-credentials/${credentialId}/deactivate`, {
    method: "PATCH",
    token,
  });
}

export function deleteModelCredential(token: string, credentialId: string): Promise<void> {
  return apiFetch<void>(`/model-credentials/${credentialId}`, {
    method: "DELETE",
    token,
  });
}
