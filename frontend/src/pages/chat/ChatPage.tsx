import { useEffect, useState, useCallback } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { api, type Thread } from "@/lib/api"
import { ThreadSidebar } from "@/components/chat/ThreadSidebar"
import { ChatPanel } from "@/components/chat/ChatPanel"

export default function ChatPage() {
  const { threadId: paramThreadId } = useParams<{ threadId?: string }>()
  const navigate = useNavigate()
  const { user, signOut } = useAuth()

  const [threads, setThreads] = useState<Thread[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  const activeThreadId = paramThreadId ? parseInt(paramThreadId, 10) : null

  const fetchThreads = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api.listThreads()
      setThreads(data)
      return data
    } catch (err) {
      console.error("Failed to fetch threads:", err)
      return []
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchThreads().then((loaded) => {
      if (!paramThreadId && loaded.length > 0) {
        navigate(`/chat/${loaded[0].id}`, { replace: true })
      }
    })
  }, [fetchThreads, paramThreadId, navigate])

  const handleCreateThread = async () => {
    setActionLoading(true)
    try {
      const newThread = await api.createThread("New Research Thread")
      setThreads((prev) => [newThread, ...prev])
      navigate(`/chat/${newThread.id}`)
    } catch (err) {
      console.error("Failed to create thread:", err)
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div className="h-screen w-screen bg-zinc-950 text-zinc-100 flex flex-col overflow-hidden">
      {/* Navbar */}
      <header className="h-12 border-b border-zinc-800/60 bg-zinc-900/70 backdrop-blur px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2.5">
          <div className="h-7 w-7 rounded-md bg-emerald-500 flex items-center justify-center">
            <span className="text-[11px] font-bold text-zinc-950 leading-none">DC</span>
          </div>
          <span className="text-[14px] font-semibold tracking-tight text-zinc-100">
            Document Copilot
          </span>
        </div>

        <div className="flex items-center space-x-3 text-[12px]">
          <span className="text-zinc-500 font-mono hidden sm:inline">{user?.email}</span>
          <button
            onClick={() => signOut()}
            className="px-2.5 py-1 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden">
        <ThreadSidebar
          threads={threads}
          activeThreadId={activeThreadId}
          onSelectThread={(id) => navigate(`/chat/${id}`)}
          onNewThread={handleCreateThread}
          loading={loading || actionLoading}
        />

        <main className="flex-1 flex flex-col h-full overflow-hidden">
          {activeThreadId ? (
            <ChatPanel key={activeThreadId} threadId={activeThreadId} />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center animate-fade-in-up">
              <div className="h-12 w-12 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-5">
                <span className="text-[17px] font-bold text-emerald-500 leading-none">DC</span>
              </div>
              <h2 className="text-lg font-semibold text-zinc-100 mb-1.5">
                Start a research thread
              </h2>
              <p className="text-[13px] text-zinc-500 max-w-xs mb-6">
                Create a new thread to ask questions about SEC 10-K filings.
              </p>
              <button
                onClick={handleCreateThread}
                disabled={actionLoading}
                className="flex items-center space-x-2 h-9 px-4 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-zinc-950 text-[13px] font-semibold rounded-lg transition-colors cursor-pointer"
              >
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                <span>New thread</span>
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
