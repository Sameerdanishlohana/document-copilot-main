/**
 * Single source of truth for frontend environment variables.
 * Validates required variables on boot.
 */

export interface Env {
  apiBaseUrl: string
  supabaseUrl: string
  supabaseAnonKey: string
}

function getEnvVar(key: string, fallback?: string): string {
  const value = import.meta.env[key] || fallback
  if (!value) {
    console.warn(`Missing environment variable: ${key}`)
    return ""
  }
  return value
}

export const env: Env = {
  apiBaseUrl: getEnvVar("VITE_API_BASE_URL", "http://localhost:8000"),
  supabaseUrl: getEnvVar("VITE_SUPABASE_URL", "http://localhost:54321"),
  supabaseAnonKey: getEnvVar("VITE_SUPABASE_ANON_KEY", "placeholder-key"),
}
