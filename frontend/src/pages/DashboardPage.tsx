import { useState } from "react"
import { useAuth } from "@/lib/auth"
import { api, ApiError } from "@/lib/api"
import { env } from "@/lib/env"

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [healthStatus, setHealthStatus] = useState<string>("Not checked")
  const [meData, setMeData] = useState<{ id: string; email: string } | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  async function checkAuthMe() {
    setLoading(true)
    setError(null)
    try {
      const data = await api.get<{ id: string; email: string }>("/auth/me")
      setMeData(data)
    } catch (err) {
      if (err instanceof ApiError && err.isNetworkError) {
        setError("Failed to connect to backend (Network / CORS error)")
      } else if (err instanceof ApiError) {
        setError(`Backend rejected with ${err.status}: ${err.message}`)
      } else {
        setError("Failed to check /auth/me")
      }
    } finally {
      setLoading(false)
    }
  }

  async function checkHealth() {
    try {
      const data = await api.get<{ status: string }>("/health")
      setHealthStatus(`OK (${data.status})`)
    } catch (err) {
      setHealthStatus("Health check failed")
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-semibold tracking-tight text-white">Document Copilot</span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">Driftwood Capital</span>
        </div>

        <div className="flex items-center space-x-4 text-xs">
          <span className="text-slate-400 font-mono">{user?.email}</span>
          <button
            onClick={() => signOut()}
            className="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold tracking-tight text-white">Authentication Verified</h2>
            <p className="text-slate-400 text-sm">
              You are signed in as an analyst. Token injection through <code className="text-indigo-400 font-mono text-xs">@/lib/api</code> is active.
            </p>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-3 font-mono text-xs">
            <div className="flex justify-between text-slate-400">
              <span>User ID:</span>
              <span className="text-slate-200 truncate max-w-[280px]">{user?.id}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Backend URL:</span>
              <span className="text-slate-200">{env.apiBaseUrl}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Public Health:</span>
              <span className="text-slate-200">{healthStatus}</span>
            </div>
            {meData && (
              <div className="pt-2 border-t border-slate-800/80 flex flex-col space-y-1">
                <span className="text-emerald-400 font-sans font-medium">✓ /auth/me Verified by FastAPI:</span>
                <span className="text-slate-300">API sees User ID: {meData.id}</span>
              </div>
            )}
            {error && (
              <div className="pt-2 border-t border-slate-800/80 text-rose-400 font-sans">
                {error}
              </div>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              onClick={checkHealth}
              className="flex-1 py-2 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs rounded-lg transition-colors cursor-pointer"
            >
              Test Public Health
            </button>
            <button
              onClick={checkAuthMe}
              disabled={loading}
              className="flex-1 py-2 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs rounded-lg transition-colors cursor-pointer"
            >
              {loading ? "Calling..." : "Test Protected /auth/me"}
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
