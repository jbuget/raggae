const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "transfer-encoding",
  "te",
  "trailer",
  "upgrade",
  "proxy-authorization",
  "proxy-authenticate",
]);

export function buildUpstreamHeaders(
  incomingHeaders: Headers,
  clientIp?: string,
): Headers {
  const headers = new Headers();

  for (const [key, value] of incomingHeaders) {
    const lower = key.toLowerCase();
    if (lower === "host" || HOP_BY_HOP.has(lower)) continue;
    headers.set(key, value);
  }

  if (clientIp) {
    headers.set("x-forwarded-for", clientIp);
  }

  return headers;
}

export function buildResponseHeaders(upstreamHeaders: Headers): Headers {
  const headers = new Headers();

  for (const [key, value] of upstreamHeaders) {
    const lower = key.toLowerCase();
    // fetch() décompresse automatiquement la réponse — ne pas retransmettre
    // Content-Encoding, sinon le browser tenterait une double décompression.
    if (lower === "content-encoding" || HOP_BY_HOP.has(lower)) continue;
    // Set-Cookie traité séparément pour éviter la déduplication de Headers
    if (lower === "set-cookie") continue;
    headers.set(key, value);
  }

  for (const cookie of upstreamHeaders.getSetCookie()) {
    headers.append("set-cookie", cookie);
  }

  return headers;
}
