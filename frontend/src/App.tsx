import { useState } from "react"
import { env } from "./lib/env"

export default function App() {
  const [status, setStatus] = useState<string>("Disconnected")

  async function checkBackend() {
    try {
      const res = await fetch(`${env.apiBaseUrl}/health`)
      const data = await res.json()
      if (data.status === "ok") {
        setStatus("Connected to Backend API")
      } else {
        setStatus("Backend return non-ok status")
      }
    } catch {
      setStatus("Failed to connect to Backend API")
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center space-x-3">
          <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
          <h1 className="text-2xl font-bold tracking-tight text-white">Document Copilot</h1>
        </div>
        <p className="text-slate-400 text-sm leading-relaxed">
          Driftwood Capital internal AI research assistant for SEC filings.
        </p>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span>API URL:</span>
            <span className="font-mono text-slate-200">{env.apiBaseUrl}</span>
          </div>
          <div className="flex justify-between text-xs text-slate-400">
            <span>Backend Connection:</span>
            <span className={`font-semibold ${status.includes("Connected") ? "text-emerald-400" : "text-amber-400"}`}>
              {status}
            </span>
          </div>
        </div>

        <button
          onClick={checkBackend}
          className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-lg transition-colors shadow-sm cursor-pointer"
        >
          Check Backend Health
        </button>
      </div>
    </div>
  )
}
