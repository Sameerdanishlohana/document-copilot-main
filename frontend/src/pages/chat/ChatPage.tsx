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
  const [loading, setLoading] = useState<boolean>(true)
  const [actionLoading, setActionLoading] = useState<boolean>(false)

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
      // If on root /chat and we have threads, navigate to the most recent one
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
    <div className="h-screen w-screen bg-slate-950 text-slate-100 flex flex-col overflow-hidden">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-semibold tracking-tight text-white">Document Copilot</span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            SEC 10-K RAG
          </span>
        </div>

        <div className="flex items-center space-x-4 text-xs">
          <span className="text-slate-400 font-mono hidden sm:inline">{user?.email}</span>
          <button
            onClick={() => signOut()}
            className="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Main split-screen layout */}
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
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4">
              <div className="text-lg font-semibold text-white">No conversation selected</div>
              <p className="text-sm text-slate-400 max-w-sm">
                Create a new chat or select an existing conversation from the sidebar to get started.
              </p>
              <button
                onClick={handleCreateThread}
                disabled={actionLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition cursor-pointer"
              >
                + Start New Conversation
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

