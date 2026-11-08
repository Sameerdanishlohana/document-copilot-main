import type { Thread } from "@/lib/api"

interface ThreadSidebarProps {
  threads: Thread[]
  activeThreadId: number | null
  onSelectThread: (id: number) => void
  onNewThread: () => void
  loading: boolean
}

function formatTime(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const mins = Math.floor((now - then) / 60000)
  if (mins < 1) return "now"
  if (mins < 60) return `${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `${days}d`
  return new Date(dateStr).toLocaleDateString(undefined, { month: "short", day: "numeric" })
}

export function ThreadSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  loading,
}: ThreadSidebarProps) {
  return (
    <aside className="w-64 border-r border-zinc-800/60 bg-zinc-900/50 flex flex-col h-full shrink-0">
      {/* New chat */}
      <div className="p-3">
        <button
          onClick={onNewThread}
          disabled={loading}
          className="w-full flex items-center justify-center space-x-2 h-9 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-40 text-zinc-200 text-[13px] font-medium rounded-lg transition-colors cursor-pointer"
        >
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>New thread</span>
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 pb-3 custom-scrollbar">
        {threads.length === 0 ? (
          <p className="text-[12px] text-zinc-600 text-center py-10 px-4">
            No conversations yet
          </p>
        ) : (
          threads.map((t, i) => {
            const active = t.id === activeThreadId
            return (
              <button
                key={t.id}
                onClick={() => onSelectThread(t.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-[13px] transition-colors cursor-pointer mb-0.5 animate-fade-in ${
                  active
                    ? "bg-zinc-800 text-zinc-100"
                    : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
                }`}
                style={{ animationDelay: `${i * 0.03}s` }}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate font-medium flex-1 mr-2">
                    {t.title || `Thread #${t.id}`}
                  </span>
                  <span className="text-[11px] text-zinc-600 shrink-0 tabular-nums">
                    {formatTime(t.updated_at)}
                  </span>
                </div>
              </button>
            )
          })
        )}
      </div>
    </aside>
  )
}
