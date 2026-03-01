import { apiFetch } from "@/lib/api/client";
import type {
  OrgModelCredentialResponse,
  SaveModelCredentialRequest,
} from "@/lib/types/api";

export function listOrgModelCredentials(
  token: string,
  organizationId: string,
): Promise<OrgModelCredentialResponse[]> {
  return apiFetch<OrgModelCredentialResponse[]>(
    `/organizations/${organizationId}/model-credentials`,
    { token },
  );
}

export function createOrgModelCredential(
  token: string,
  organizationId: string,
  data: SaveModelCredentialRequest,
): Promise<OrgModelCredentialResponse> {
  return apiFetch<OrgModelCredentialResponse>(
    `/organizations/${organizationId}/model-credentials`,
    { method: "POST", token, body: JSON.stringify(data) },
  );
}

export function activateOrgModelCredential(
  token: string,
  organizationId: string,
  credentialId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/model-credentials/${credentialId}/activate`,
    { method: "PATCH", token },
  );
}

export function deactivateOrgModelCredential(
  token: string,
  organizationId: string,
  credentialId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/model-credentials/${credentialId}/deactivate`,
    { method: "PATCH", token },
  );
}

export function deleteOrgModelCredential(
  token: string,
  organizationId: string,
  credentialId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/model-credentials/${credentialId}`,
    { method: "DELETE", token },
  );
}
