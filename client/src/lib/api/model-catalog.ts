import { apiFetch } from "@/lib/api/client";
import type { ModelCatalogResponse } from "@/lib/types/api";

export function getModelCatalog(token: string): Promise<ModelCatalogResponse> {
  return apiFetch<ModelCatalogResponse>("/model-catalog", { token });
}
