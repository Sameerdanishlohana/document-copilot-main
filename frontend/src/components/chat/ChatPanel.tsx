import { useEffect, useRef, useState, useMemo } from "react"
import { useChat } from "@ai-sdk/react"
import { DefaultChatTransport, type UIMessage } from "ai"
import { env } from "@/lib/env"
import { supabase } from "@/lib/supabase"
import { api, type ChatMessageItem } from "@/lib/api"
import { CitationChip, type Citation } from "./CitationChip"
import { SourcePassagePanel } from "./SourcePassagePanel"

interface ChatPanelProps {
  threadId: number
}

export function ChatPanel({ threadId }: ChatPanelProps) {
  const [initialLoading, setInitialLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [inputMessage, setInputMessage] = useState("")
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const transport = useMemo(() => {
    return new DefaultChatTransport({
      api: `${env.apiBaseUrl.replace(/\/+$/, "")}/chat/stream`,
      headers: async (): Promise<Record<string, string>> => {
        const { data } = await supabase.auth.getSession()
        const token = data.session?.access_token
        const h: Record<string, string> = {}
        if (token) h["Authorization"] = `Bearer ${token}`
        return h
      },
      body: { threadId },
    })
  }, [threadId])

  const { messages, setMessages, sendMessage, status, error } = useChat({
    id: `thread-${threadId}`,
    transport,
  })

  useEffect(() => {
    let cancelled = false
    setInitialLoading(true)
    setLoadError(null)

    api.getThreadMessages(threadId)
      .then((history: ChatMessageItem[]) => {
        if (cancelled) return
        const formatted: UIMessage[] = history.map((item) => {
          const citations: Citation[] =
            Array.isArray(item.message_json?.citations) ? (item.message_json.citations as Citation[]) : []

          const parts: UIMessage["parts"] = [{ type: "text", text: item.content }]
          if (citations.length > 0) {
            parts.push({
              type: "data",
              data: { type: "citations", citations },
            } as any)
          }

          return {
            id: String(item.id),
            role: item.role,
            parts,
          }
        })
        setMessages(formatted)
        setInitialLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        setLoadError(err instanceof Error ? err.message : "Failed to load history")
        setInitialLoading(false)
      })

    return () => { cancelled = true }
  }, [threadId, setMessages])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, status])

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto"
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 150) + "px"
    }
  }, [inputMessage])

  const busy = status === "submitted" || status === "streaming"

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault()
    const trimmed = inputMessage.trim()
    if (!trimmed || busy) return
    setInputMessage("")
    await sendMessage({ text: trimmed })
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex h-full overflow-hidden">
      <div className="flex-1 flex flex-col h-full bg-zinc-950">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="max-w-2xl mx-auto px-5 py-6 space-y-6">
            {initialLoading ? (
              <div className="flex items-center justify-center pt-24 animate-fade-in">
                <div className="h-5 w-5 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin" />
              </div>
            ) : loadError ? (
              <div className="mt-12 p-3.5 bg-red-500/5 border border-red-500/10 rounded-lg animate-fade-in">
                <p className="text-[13px] text-red-400">{loadError}</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center pt-24 animate-fade-in-up">
                <div className="h-10 w-10 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
                  <span className="text-[15px] font-bold text-emerald-500 leading-none">DC</span>
                </div>
                <h3 className="text-[15px] font-semibold text-zinc-100 mb-1.5">
                  What would you like to research?
                </h3>
                <p className="text-[13px] text-zinc-500 text-center max-w-xs mb-8">
                  Ask about revenue, risk factors, segment data, or anything in the 10-K filings.
                </p>
                <div className="flex flex-wrap justify-center gap-2 max-w-md">
                  {[
                    "Apple's FY2024 revenue breakdown",
                    "NVDA vs MSFT R&D spend",
                    "Alphabet risk factors summary",
                  ].map((q, i) => (
                    <button
                      key={q}
                      onClick={() => setInputMessage(q)}
                      className="text-[12px] px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700 transition-colors cursor-pointer animate-fade-in"
                      style={{ animationDelay: `${0.2 + i * 0.08}s` }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((m, i) => {
                  const isUser = m.role === "user"
                  const text = m.parts
                    ?.filter((p): p is { type: "text"; text: string } => p.type === "text")
                    .map((p) => p.text)
                    .join("") || ""

                  // Extract citations from custom data parts or metadata
                  const citations: Citation[] = []
                  for (const part of (m.parts as any[]) || []) {
                    if (part.type === "data" && part.data?.type === "citations") {
                      const list = part.data.citations
                      if (Array.isArray(list)) citations.push(...list)
                    } else if (part.type?.startsWith("data-") && part.data?.citations) {
                      const list = part.data.citations
                      if (Array.isArray(list)) citations.push(...list)
                    }
                  }

                  return (
                    <div
                      key={m.id}
                      className="animate-fade-in"
                      style={{ animationDelay: `${i * 0.04}s` }}
                    >
                      {/* Role label */}
                      <div className={`text-[11px] font-medium mb-1.5 ${
                        isUser ? "text-zinc-500" : "text-emerald-500/80"
                      }`}>
                        {isUser ? "You" : "Document Copilot"}
                      </div>

                      {/* Message body */}
                      <div className={`text-[14px] leading-relaxed whitespace-pre-wrap ${
                        isUser
                          ? "text-zinc-100 pl-0"
                          : "text-zinc-300 border-l-2 border-zinc-800 pl-4"
                      }`}>
                        {text}
                      </div>

                      {/* Citation chips */}
                      {!isUser && citations.length > 0 && (
                        <div className="pl-4 mt-3 flex flex-wrap gap-2 items-center">
                          <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider">
                            Sources:
                          </span>
                          {citations.map((c, cIdx) => (
                            <CitationChip
                              key={cIdx}
                              citation={c}
                              index={cIdx}
                              isSelected={selectedCitation?.excerpt === c.excerpt}
                              onSelect={(selected) =>
                                setSelectedCitation((prev) => (prev?.excerpt === selected.excerpt ? null : selected))
                              }
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  )
                })}

                {/* Typing indicator */}
                {busy && messages[messages.length - 1]?.role !== "assistant" && (
                  <div className="animate-fade-in">
                    <div className="text-[11px] font-medium text-emerald-500/80 mb-1.5">
                      Document Copilot
                    </div>
                    <div className="border-l-2 border-zinc-800 pl-4 flex items-center space-x-1">
                      <div className="h-1.5 w-1.5 rounded-full bg-zinc-500 typing-dot-1" />
                      <div className="h-1.5 w-1.5 rounded-full bg-zinc-500 typing-dot-2" />
                      <div className="h-1.5 w-1.5 rounded-full bg-zinc-500 typing-dot-3" />
                    </div>
                  </div>
                )}
              </>
            )}

            {error && (
              <div className="p-3 bg-red-500/5 border border-red-500/10 rounded-lg animate-fade-in">
                <p className="text-[13px] text-red-400">{error.message}</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-zinc-800/60 bg-zinc-950 p-4">
          <form onSubmit={handleSend} className="max-w-2xl mx-auto">
            <div className="flex items-end gap-2 bg-zinc-900 border border-zinc-800 rounded-xl focus-within:border-zinc-700 transition-colors">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about SEC filings…"
                disabled={initialLoading || busy}
                rows={1}
                className="flex-1 resize-none bg-transparent px-4 py-3 text-[14px] text-zinc-100 placeholder-zinc-600 outline-none disabled:opacity-50 max-h-[150px]"
              />
              <div className="pr-2 pb-2">
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || initialLoading || busy}
                  className="h-8 w-8 flex items-center justify-center bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-zinc-950 rounded-lg transition-colors cursor-pointer"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-[11px] text-zinc-700 text-center mt-2">
              Every factual assertion is grounded and backed by SEC 10-K citations
            </p>
          </form>
        </div>
      </div>

      {/* Side panel for source passage verification */}
      <SourcePassagePanel
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  )
}
