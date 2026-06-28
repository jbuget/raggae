export function getSafeAuthCallbackUrl(value: string | null) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) {
    return "/projects";
  }
  return value;
}

export function buildAuthRedirectPath(path: "/login" | "/register", callbackUrl: string | null) {
  const safeCallbackUrl = getSafeAuthCallbackUrl(callbackUrl);
  if (!callbackUrl || safeCallbackUrl === "/projects") {
    return path;
  }
  return `${path}?callbackUrl=${encodeURIComponent(safeCallbackUrl)}`;
}
