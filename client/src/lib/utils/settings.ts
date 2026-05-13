/**
 * Resolve the effective value for a string field that uses "none" as a sentinel
 * for absent/empty values. Priority: local state → fallback chain.
 * `undefined` local means untouched by the user; `null` or `""` mean explicitly cleared.
 */
export function resolveStringField(
  local: string | null | undefined,
  ...chain: (string | null | undefined)[]
): string {
  const raw = local !== undefined ? local : chain.find((v) => v != null);
  return raw || "none";
}

/**
 * Resolve the effective value for a nullable field (numeric, boolean).
 * Priority: local state → fallback chain. Returns null when nothing is set.
 * `undefined` local means untouched; `null` local means explicitly cleared (stops chain lookup).
 */
export function resolveField<T>(
  local: T | null | undefined,
  ...chain: (T | null | undefined)[]
): T | null {
  if (local !== undefined) return local ?? null;
  for (const val of chain) {
    if (val != null) return val;
  }
  return null;
}
