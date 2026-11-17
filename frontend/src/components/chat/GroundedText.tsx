import React from "react"
import type { Citation } from "./CitationChip"

interface GroundedTextProps {
  text: string
  citations: Citation[]
  onSelectCitation: (citation: Citation) => void
  selectedCitation: Citation | null
}

/**
 * Parses assistant text and renders inline citation markers [1], [2] as interactive buttons.
 */
export function GroundedText({
  text,
  citations,
  onSelectCitation,
  selectedCitation,
}: GroundedTextProps) {
  if (!citations || citations.length === 0) {
    return <span>{text}</span>
  }

  // Regex matches [1], [2], [1, 2], [1][2] citation patterns in assistant text
  const citationRegex = /\[(\d+)\]/g
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = citationRegex.exec(text)) !== null) {
    const start = match.index
    const end = citationRegex.lastIndex
    const citeNumber = parseInt(match[1], 10)
    const citationIndex = citeNumber - 1

    // Add preceding plain text
    if (start > lastIndex) {
      parts.push(text.slice(lastIndex, start))
    }

    const citation = citations[citationIndex]

    if (citation) {
      const isSelected = selectedCitation?.excerpt === citation.excerpt
      parts.push(
        <button
          key={`cite-${start}-${citeNumber}`}
          type="button"
          onClick={() => onSelectCitation(citation)}
          className={`inline-flex items-center justify-center font-mono font-semibold text-[11px] px-1 py-0.5 mx-0.5 rounded cursor-pointer transition-all align-baseline ${
            isSelected
              ? "bg-emerald-500 text-zinc-950 ring-2 ring-emerald-400"
              : "bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 hover:bg-emerald-900/60 hover:text-emerald-300"
          }`}
          title={`Source: ${citation.company} (${citation.filing_type} ${citation.section || ""})`}
        >
          [{citeNumber}]
        </button>
      )
    } else {
      // Citation number out of bounds - render as plain text
      parts.push(match[0])
    }

    lastIndex = end
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }

  return <>{parts}</>
}
