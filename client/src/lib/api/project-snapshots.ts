import type {
  ProjectSnapshotListResponse,
  ProjectSnapshotResponse,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function listProjectSnapshots(
  token: string,
  projectId: string,
  limit = 20,
  offset = 0,
): Promise<ProjectSnapshotListResponse> {
  return apiFetch<ProjectSnapshotListResponse>(
    `/projects/${projectId}/snapshots?limit=${limit}&offset=${offset}`,
    { token },
  );
}

export function getProjectSnapshot(
  token: string,
  projectId: string,
  versionNumber: number,
): Promise<ProjectSnapshotResponse> {
  return apiFetch<ProjectSnapshotResponse>(
    `/projects/${projectId}/snapshots/${versionNumber}`,
    { token },
  );
}

export function restoreProjectSnapshot(
  token: string,
  projectId: string,
  versionNumber: number,
): Promise<ProjectSnapshotResponse> {
  return apiFetch<ProjectSnapshotResponse>(
    `/projects/${projectId}/snapshots/${versionNumber}/restore`,
    { method: "POST", token },
  );
}
