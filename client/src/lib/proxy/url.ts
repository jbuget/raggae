export function buildUpstreamUrl(
  backendUrl: string,
  path: string[],
  searchParams: URLSearchParams,
): string {
  const base = backendUrl.endsWith("/") ? backendUrl.slice(0, -1) : backendUrl;
  const fullPath = `/api/v1/${path.join("/")}`;
  const query = searchParams.toString();
  return query ? `${base}${fullPath}?${query}` : `${base}${fullPath}`;
}
