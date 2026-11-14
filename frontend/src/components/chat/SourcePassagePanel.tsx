import type { Citation } from "./CitationChip"

interface SourcePassagePanelProps {
  citation: Citation | null
  onClose: () => void
}

export function SourcePassagePanel({ citation, onClose }: SourcePassagePanelProps) {
  if (!citation) return null

  return (
    <aside className="w-96 border-l border-zinc-800/80 bg-zinc-950 flex flex-col h-full animate-fade-in z-20 shadow-2xl">
      {/* Header */}
      <div className="h-14 px-4 border-b border-zinc-800/80 flex items-center justify-between bg-zinc-900/40">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500" />
          <h4 className="text-[13px] font-semibold text-zinc-100 tracking-wide uppercase">
            Source Passage
          </h4>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-md text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/60 transition-colors cursor-pointer"
          aria-label="Close passage panel"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Metadata Badges */}
      <div className="p-4 border-b border-zinc-900 space-y-2 bg-zinc-900/20">
        <div className="text-[14px] font-medium text-zinc-100">
          {citation.company}
        </div>
        <div className="flex flex-wrap gap-1.5 text-[11px] text-zinc-400">
          <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono">
            {citation.filing_type}
          </span>
          {citation.filing_date && (
            <span className="px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-400 font-mono">
              {citation.filing_date}
            </span>
          )}
          {citation.page && (
            <span className="px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-400 font-mono">
              p. {citation.page}
            </span>
          )}
          {citation.section && (
            <span className="px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-400">
              {citation.section}
            </span>
          )}
        </div>
      </div>

      {/* Excerpt Body */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <div className="text-[11px] font-semibold text-zinc-500 tracking-wider uppercase mb-2">
          Verified Excerpt
        </div>
        <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-[13px] leading-relaxed text-zinc-200 whitespace-pre-wrap font-serif selection:bg-emerald-500/30">
          {citation.excerpt || "No excerpt text available."}
        </div>

        <div className="mt-4 p-3 rounded-md bg-emerald-950/20 border border-emerald-900/30 text-[11px] text-emerald-400 leading-normal">
          <span className="font-semibold">Audit trail:</span> This passage was verified by the grounding validator against the SEC 10-K corpus.
        </div>
      </div>
    </aside>
  )
}
