export interface Citation {
  chunk_id?: number
  company: string
  filing_type: string
  filing_date?: string
  page?: string
  section?: string
  excerpt: string
}

interface CitationChipProps {
  citation: Citation
  index: number
  onSelect: (citation: Citation) => void
  isSelected?: boolean
}

export function CitationChip({ citation, index, onSelect, isSelected = false }: CitationChipProps) {
  const label = [
    citation.company || "Filing",
    citation.filing_type || "10-K",
    citation.section || (citation.page ? `p. ${citation.page}` : null),
  ]
    .filter(Boolean)
    .join(" · ")

  return (
    <button
      type="button"
      onClick={() => onSelect(citation)}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-mono transition-all cursor-pointer border ${
        isSelected
          ? "bg-emerald-950/70 text-emerald-300 border-emerald-600/70 shadow-sm shadow-emerald-950/50"
          : "bg-zinc-900/90 text-zinc-300 border-zinc-800 hover:border-emerald-500/40 hover:text-emerald-300"
      }`}
      title="Click to inspect source passage"
    >
      <span className="text-[10px] font-sans px-1 py-0.2 rounded bg-zinc-800 text-zinc-400 font-semibold">
        [{index + 1}]
      </span>
      <span className="truncate max-w-[200px]">{label}</span>
    </button>
  )
}
