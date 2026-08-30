import { env } from "./env"
import { supabase } from "./supabase"

export class ApiError extends Error {
  public status: number
  public isNetworkError: boolean
  public data: unknown

  constructor(message: string, status: number = 0, isNetworkError: boolean = false, data?: unknown) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.isNetworkError = isNetworkError
    this.data = data
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const url = `${env.apiBaseUrl.replace(/\/+$/, "")}/${endpoint.replace(/^\/+/, "")}`

  const headers = new Headers(options.headers || {})
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  // Inject Supabase JWT auth token if user is signed in
  try {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (token && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`)
    }
  } catch (err) {
    console.warn("Failed to retrieve Supabase session token:", err)
  }

  let body: BodyInit | undefined = undefined
  if (options.body !== undefined) {
    if (options.body instanceof FormData || typeof options.body === "string") {
      body = options.body
    } else {
      body = JSON.stringify(options.body)
    }
  }

  let response: Response
  try {
    response = await fetch(url, {
      ...options,
      headers,
      body,
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : "Network error"
    throw new ApiError(message, 0, true)
  }

  let data: unknown
  const contentType = response.headers.get("content-type")
  if (contentType && contentType.includes("application/json")) {
    try {
      data = await response.json()
    } catch {
      data = null
    }
  } else {
    try {
      data = await response.text()
    } catch {
      data = null
    }
  }

  if (!response.ok) {
    const errorMessage =
      data && typeof data === "object" && "detail" in data && typeof data.detail === "string"
        ? data.detail
        : `HTTP request failed with status ${response.status}`
    throw new ApiError(errorMessage, response.status, false, data)
  }

  return data as T
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) => request<T>(endpoint, { ...options, method: "GET" }),
  post: <T>(endpoint: string, body?: unknown, options?: RequestOptions) => request<T>(endpoint, { ...options, method: "POST", body }),
  put: <T>(endpoint: string, body?: unknown, options?: RequestOptions) => request<T>(endpoint, { ...options, method: "PUT", body }),
  patch: <T>(endpoint: string, body?: unknown, options?: RequestOptions) => request<T>(endpoint, { ...options, method: "PATCH", body }),
  delete: <T>(endpoint: string, options?: RequestOptions) => request<T>(endpoint, { ...options, method: "DELETE" }),
}
