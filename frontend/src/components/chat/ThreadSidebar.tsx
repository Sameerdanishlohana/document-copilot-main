import type { Thread } from "@/lib/api"

interface ThreadSidebarProps {
  threads: Thread[]
  activeThreadId: number | null
  onSelectThread: (id: number) => void
  onNewThread: () => void
  loading: boolean
}

export function ThreadSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  loading,
}: ThreadSidebarProps) {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
          Conversations
        </span>
        <button
          onClick={onNewThread}
          disabled={loading}
          className="text-xs px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-md font-medium transition cursor-pointer"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {threads.length === 0 ? (
          <div className="text-xs text-slate-500 p-4 text-center">
            No chats yet. Start one above!
          </div>
        ) : (
          threads.map((t) => {
            const isActive = t.id === activeThreadId
            return (
              <button
                key={t.id}
                onClick={() => onSelectThread(t.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-xs truncate transition flex items-center space-x-2 cursor-pointer ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-200 border border-indigo-500/30 font-medium"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <span className="truncate flex-1">{t.title || `Chat #${t.id}`}</span>
              </button>
            )
          })
        )}
      </div>
    </aside>
  )
}

