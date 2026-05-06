import { API_BASE_URL } from "../config";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit;
  json?: unknown;
};

async function request<T>(path: string, init: RequestOptions = {}): Promise<T> {
  const { json, headers, ...rest } = init;

  const finalHeaders = new Headers(headers);
  let body: BodyInit | undefined = init.body;
  if (json !== undefined) {
    finalHeaders.set("Content-Type", "application/json");
    body = JSON.stringify(json);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
    body,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const data = await response.json();
      if (data && typeof data === "object" && "detail" in data) {
        message = String(data.detail);
      }
    } catch {
      /* ignore parse errors */
    }
    throw new ApiError(response.status, message || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string, init?: RequestOptions) =>
    request<T>(path, { ...init, method: "GET" }),
  post: <T>(path: string, init?: RequestOptions) =>
    request<T>(path, { ...init, method: "POST" }),
  patch: <T>(path: string, init?: RequestOptions) =>
    request<T>(path, { ...init, method: "PATCH" }),
  delete: <T>(path: string, init?: RequestOptions) =>
    request<T>(path, { ...init, method: "DELETE" }),
};

export const buildUrl = (path: string): string => `${API_BASE_URL}${path}`;
