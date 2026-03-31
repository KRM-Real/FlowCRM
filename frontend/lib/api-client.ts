import { API_BASE_URL } from "@/lib/env";

type ApiRequestOptions = RequestInit & {
  skipAuthRefresh?: boolean;
};

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function parseResponse(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

export async function apiFetch<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { skipAuthRefresh = false, headers, ...init } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });

  if (response.status === 401 && !skipAuthRefresh && path !== "/api/auth/refresh/") {
    const refreshResponse = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (refreshResponse.ok) {
      return apiFetch<T>(path, { ...options, skipAuthRefresh: true });
    }
  }

  if (!response.ok) {
    const details = await parseResponse(response);
    const message =
      typeof details === "object" &&
      details !== null &&
      "detail" in details &&
      typeof details.detail === "string"
        ? details.detail
        : "Request failed.";

    throw new ApiError(message, response.status, details);
  }

  if (response.status === 204 || response.status === 205) {
    return null as T;
  }

  return (await parseResponse(response)) as T;
}
