export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {},
): Promise<T> {
  const { token, headers: customHeaders, ...fetchOptions } = options;

  const headers: Record<string, string> = {};

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (
    fetchOptions.body &&
    typeof fetchOptions.body === "string"
  ) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`/api/v1${path}`, {
    ...fetchOptions,
    headers: {
      ...headers,
      ...(customHeaders as Record<string, string>),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    let message: string;
    try {
      const json = JSON.parse(text);
      message = json.detail || json.message || text;
    } catch {
      message = text;
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
