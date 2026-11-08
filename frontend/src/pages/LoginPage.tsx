import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { supabase } from "@/lib/supabase"

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/"

  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)

    try {
      if (isSignUp) {
        const { data, error: signUpError } = await supabase.auth.signUp({ email, password })
        if (signUpError) { setError(signUpError.message); return }
        if (data.session) {
          navigate(from, { replace: true })
        } else {
          setMessage("Account created. Check your inbox if email confirmation is enabled.")
        }
      } else {
        const { error: signInError } = await supabase.auth.signInWithPassword({ email, password })
        if (signInError) { setError(signInError.message); return }
        navigate(from, { replace: true })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex">
      {/* Left — branding half */}
      <div className="hidden lg:flex lg:w-[45%] bg-zinc-900 border-r border-zinc-800/60 flex-col justify-between p-12">
        <div>
          {/* Logo row */}
          <div className="flex items-center space-x-2.5 mb-20">
            <div className="h-8 w-8 rounded-md bg-emerald-500 flex items-center justify-center">
              <span className="text-[13px] font-bold text-zinc-950 leading-none">DC</span>
            </div>
            <span className="text-[15px] font-semibold tracking-tight text-zinc-100">
              Document Copilot
            </span>
          </div>

          {/* Headline */}
          <div className="max-w-sm space-y-5 animate-fade-in-up">
            <h2 className="text-[28px] font-semibold leading-[1.2] tracking-tight text-white">
              Research SEC filings
              <br />
              with cited AI answers.
            </h2>
            <p className="text-[15px] leading-relaxed text-zinc-400">
              Ask questions across 10-K filings for AAPL, MSFT, NVDA, AMZN, and GOOGL.
              Every claim links back to its source passage.
            </p>

            {/* Compact feature list */}
            <div className="pt-4 space-y-3">
              {[
                "Hybrid semantic + keyword retrieval",
                "Inline source citations on every answer",
                "Real-time streamed responses",
              ].map((text, i) => (
                <div
                  key={text}
                  className="flex items-center space-x-3 text-[13px] text-zinc-300 animate-fade-in"
                  style={{ animationDelay: `${0.3 + i * 0.1}s` }}
                >
                  <div className="h-1 w-1 rounded-full bg-emerald-500 shrink-0" />
                  <span>{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="text-[11px] text-zinc-600">
          Driftwood Capital · Internal Research Tool
        </p>
      </div>

      {/* Right — form half */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-[380px] animate-scale-in">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center space-x-2.5 mb-10">
            <div className="h-8 w-8 rounded-md bg-emerald-500 flex items-center justify-center">
              <span className="text-[13px] font-bold text-zinc-950 leading-none">DC</span>
            </div>
            <span className="text-[15px] font-semibold tracking-tight">Document Copilot</span>
          </div>

          {/* Heading */}
          <div className="mb-8">
            <h1 className="text-xl font-semibold tracking-tight text-white">
              {isSignUp ? "Create an account" : "Sign in"}
            </h1>
            <p className="text-sm text-zinc-500 mt-1">
              {isSignUp ? "Get started with filing research" : "Continue your research"}
            </p>
          </div>

          {/* Alerts */}
          {error && (
            <div className="mb-5 px-3.5 py-3 bg-red-500/5 border border-red-500/10 rounded-lg animate-fade-in">
              <p className="text-[13px] text-red-400">{error}</p>
            </div>
          )}
          {message && (
            <div className="mb-5 px-3.5 py-3 bg-emerald-500/5 border border-emerald-500/10 rounded-lg animate-fade-in">
              <p className="text-[13px] text-emerald-400">{message}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-medium text-zinc-400 mb-1.5" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full h-10 px-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-zinc-100 placeholder-zinc-600 outline-none focus:border-zinc-600 transition-colors"
              />
            </div>

            <div>
              <label className="block text-[12px] font-medium text-zinc-400 mb-1.5" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full h-10 px-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-zinc-100 placeholder-zinc-600 outline-none focus:border-zinc-600 transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-10 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-zinc-950 font-semibold text-sm rounded-lg transition-colors cursor-pointer relative"
            >
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-4 w-4 border-2 border-zinc-950/20 border-t-zinc-950 rounded-full animate-spin" />
                </div>
              ) : (
                isSignUp ? "Create account" : "Sign in"
              )}
            </button>
          </form>

          {/* Toggle */}
          <div className="mt-6 pt-5 border-t border-zinc-800/60 text-center">
            <button
              type="button"
              onClick={() => { setIsSignUp(!isSignUp); setError(null); setMessage(null) }}
              className="text-[13px] text-zinc-500 hover:text-zinc-300 transition-colors cursor-pointer"
            >
              {isSignUp
                ? <>Have an account? <span className="text-zinc-200 font-medium">Sign in</span></>
                : <>Need an account? <span className="text-zinc-200 font-medium">Sign up</span></>}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
