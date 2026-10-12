import type { ApiErrorBody } from "../types";
import { ApiError } from "./errors";
import type { TokenStore } from "./tokenStore";
import { MemoryTokenStore } from "./tokenStore";

const PUBLIC_AUTH_PATHS = new Set([
  "/auth/initiate-register",
  "/auth/complete-register",
  "/auth/login",
  "/auth/logout",
  "/auth/refresh",
  "/auth/forgot-password",
  "/auth/reset-password",
]);

export interface ApiClientOptions {
  /** Gateway origin, e.g. http://localhost:8000 */
  baseUrl?: string;
  tokenStore?: TokenStore;
  fetch?: typeof fetch;
}

function joinUrl(baseUrl: string, path: string): string {
  const base = baseUrl.replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

function toQuery(
  params?: Record<string, string | number | boolean | null | undefined>,
): string {
  if (!params) {
    return "";
  }
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    search.set(key, String(value));
  }
  const encoded = search.toString();
  return encoded ? `?${encoded}` : "";
}

async function parseBody(response: Response): Promise<unknown> {
  if (response.status === 204 || response.status === 205) {
    return undefined;
  }
  const text = await response.text();
  if (!text) {
    return undefined;
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as ApiErrorBody).detail;
    if (typeof detail === "string") {
      return detail;
    }
    return JSON.stringify(detail);
  }
  return `Request failed with status ${status}`;
}

export class ApiClient {
  readonly baseUrl: string;
  readonly tokenStore: TokenStore;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ApiClientOptions = {}) {
    const fromEnv =
      typeof import.meta !== "undefined"
        ? import.meta.env?.VITE_API_BASE_URL
        : undefined;
    this.baseUrl = options.baseUrl ?? fromEnv ?? "http://localhost:8000";
    this.tokenStore = options.tokenStore ?? new MemoryTokenStore();
    this.fetchImpl = options.fetch ?? fetch.bind(globalThis);
  }

  async request<T>(
    method: string,
    path: string,
    options: {
      query?: Record<string, string | number | boolean | null | undefined>;
      body?: unknown;
      auth?: boolean;
      headers?: Record<string, string>;
    } = {},
  ): Promise<T> {
    const pathname = path.split("?")[0] ?? path;
    const auth = options.auth ?? !PUBLIC_AUTH_PATHS.has(pathname);
    const headers: Record<string, string> = { ...options.headers };

    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    if (auth) {
      const token = this.tokenStore.getAccessToken();
      if (!token) {
        throw new ApiError(401, "Missing access token");
      }
      headers.Authorization = `Bearer ${token}`;
    }

    const url = `${joinUrl(this.baseUrl, path)}${toQuery(options.query)}`;
    const response = await this.fetchImpl(url, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    const parsed = await parseBody(response);

    if (!response.ok) {
      const body =
        parsed && typeof parsed === "object" && "detail" in parsed
          ? (parsed as ApiErrorBody)
          : null;
      throw new ApiError(response.status, errorMessage(response.status, parsed), body);
    }

    return parsed as T;
  }

  get<T>(
    path: string,
    query?: Record<string, string | number | boolean | null | undefined>,
    auth?: boolean,
  ): Promise<T> {
    return this.request<T>("GET", path, { query, auth });
  }

  post<T>(path: string, body?: unknown, auth?: boolean): Promise<T> {
    return this.request<T>("POST", path, { body, auth });
  }

  patch<T>(path: string, body?: unknown, auth?: boolean): Promise<T> {
    return this.request<T>("PATCH", path, { body, auth });
  }

  delete<T>(path: string, auth?: boolean): Promise<T> {
    return this.request<T>("DELETE", path, { auth });
  }
}
