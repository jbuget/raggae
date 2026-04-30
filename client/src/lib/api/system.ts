import type { SystemDefaultsResponse } from "@/lib/types/api";
import { apiFetch } from "./client";

export function getSystemDefaults(): Promise<SystemDefaultsResponse> {
  return apiFetch<SystemDefaultsResponse>("/system/defaults");
}
