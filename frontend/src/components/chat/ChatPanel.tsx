import { useEffect, useRef, useState, useMemo } from "react"
import { useChat } from "@ai-sdk/react"
import { DefaultChatTransport, type UIMessage } from "ai"
import { env } from "@/lib/env"
import { supabase } from "@/lib/supabase"
import { api, type ChatMessageItem } from "@/lib/api"

interface ChatPanelProps {
  threadId: number
}

export function ChatPanel({ threadId }: ChatPanelProps) {
  const [initialLoading, setInitialLoading] = useState<boolean>(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [inputMessage, setInputMessage] = useState<string>("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Configure AI SDK transport with FastAPI backend URL and user JWT
  const transport = useMemo(() => {
    return new DefaultChatTransport({
      api: `${env.apiBaseUrl.replace(/\/+$/, "")}/chat/stream`,
      headers: async (): Promise<Record<string, string>> => {
        const { data } = await supabase.auth.getSession()
        const token = data.session?.access_token
        const headers: Record<string, string> = {}
        if (token) {
          headers["Authorization"] = `Bearer ${token}`
        }
        return headers
      },
      body: {
        threadId,
      },
    })
  }, [threadId])

  const { messages, setMessages, sendMessage, status, error } = useChat({
    id: `thread-${threadId}`,
    transport,
  })

  // Load message history on thread change
  useEffect(() => {
    let cancelled = false
    setInitialLoading(true)
    setLoadError(null)

    api.getThreadMessages(threadId)
      .then((history: ChatMessageItem[]) => {
        if (cancelled) return
        const formatted: UIMessage[] = history.map((item) => ({
          id: String(item.id),
          role: item.role,
          parts: [{ type: "text", text: item.content }],
        }))
        setMessages(formatted)
        setInitialLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setLoadError(err instanceof Error ? err.message : "Failed to load thread history")
        setInitialLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [threadId, setMessages])

  // Scroll to bottom on message updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, status])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = inputMessage.trim()
    if (!trimmed || status === "submitted" || status === "streaming") return

    setInputMessage("")
    await sendMessage({
      text: trimmed,
    })
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {initialLoading ? (
          <div className="text-center text-slate-500 text-sm mt-12 animate-pulse">
            Loading conversation history...
          </div>
        ) : loadError ? (
          <div className="p-4 bg-rose-950/40 border border-rose-800 text-rose-300 text-sm rounded-lg">
            {loadError}
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-16 max-w-md mx-auto space-y-2">
            <div className="text-slate-400 font-medium">Ready to analyze filings</div>
            <p className="text-xs">
              Ask questions about 10-K filings (e.g. Apple, Microsoft, Nvidia revenue, risks, or segment data).
            </p>
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.role === "user"
            const textContent =
              m.parts
                ?.filter((p): p is { type: "text"; text: string } => p.type === "text")
                .map((p) => p.text)
                .join("") ||
              ""

            return (
              <div
                key={m.id}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                <div className="text-[11px] font-mono text-slate-500 mb-1 px-1">
                  {isUser ? "You" : "Document Copilot"}
                </div>
                <div
                  className={`max-w-2xl px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                      ? "bg-indigo-600 text-white rounded-br-none"
                      : "bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-md"
                  }`}
                >
                  {textContent}
                </div>
              </div>
            )
          })
        )}

        {status === "streaming" && (
          <div className="flex items-center space-x-2 text-indigo-400 text-xs px-2 py-1">
            <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
            <span className="font-mono">Streaming response...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-300 text-xs rounded-lg">
            Error: {error.message}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/40">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto flex space-x-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask a question about the financial filings..."
            disabled={initialLoading || status === "submitted" || status === "streaming"}
            className="flex-1 bg-slate-900 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={
              !inputMessage.trim() ||
              initialLoading ||
              status === "submitted" ||
              status === "streaming"
            }
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition cursor-pointer shrink-0"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
