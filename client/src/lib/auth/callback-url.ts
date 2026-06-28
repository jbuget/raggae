export function getSafeAuthCallbackUrl(value: string | null) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) {
    return "/projects";
  }
  return value;
}

export function buildAuthRedirectPath(path: "/login" | "/register", callbackUrl: string | null) {
  if (!callbackUrl) {
    return path;
  }
  const safeCallbackUrl = getSafeAuthCallbackUrl(callbackUrl);
  return `${path}?callbackUrl=${encodeURIComponent(safeCallbackUrl)}`;
}
