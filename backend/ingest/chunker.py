"""Chunking module for SEC 10-K Markdown filings.

Splits normalized Markdown filings into retrieval-sized chunks (~500-800 tokens)
with overlap, tracking section headers and chunk indices.
"""

from dataclasses import dataclass
import re
import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")


@dataclass
class DocumentChunk:
    chunk_index: int
    text: str
    token_count: int
    section: str | None = None
    page: str | None = None


def count_tokens(text: str) -> int:
    """Return the number of tokens in text using cl100k_base tokenizer."""
    return len(_ENCODER.encode(text))


def chunk_markdown(
    markdown_text: str,
    target_tokens: int = 600,
    overlap_tokens: int = 100,
) -> list[DocumentChunk]:
    """Split Markdown text into overlapping chunks while preserving section context.

    Splits primarily across double newlines / paragraph boundaries, keeping
    track of the most recent header as the current section.
    """
    if not markdown_text or not markdown_text.strip():
        return []

    lines = markdown_text.splitlines()
    paragraphs: list[tuple[str, str | None]] = []
    current_section: str | None = None

    header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    buffer_lines: list[str] = []

    for line in lines:
        header_match = header_pattern.match(line.strip())
        if header_match:
            # Flush previous buffer
            if buffer_lines:
                text_block = "\n".join(buffer_lines).strip()
                if text_block:
                    paragraphs.append((text_block, current_section))
                buffer_lines = []
            current_section = header_match.group(2).strip()
            buffer_lines.append(line)
        elif not line.strip():
            if buffer_lines:
                text_block = "\n".join(buffer_lines).strip()
                if text_block:
                    paragraphs.append((text_block, current_section))
                buffer_lines = []
        else:
            buffer_lines.append(line)

    if buffer_lines:
        text_block = "\n".join(buffer_lines).strip()
        if text_block:
            paragraphs.append((text_block, current_section))

    chunks: list[DocumentChunk] = []
    current_chunk_parts: list[str] = []
    current_chunk_section: str | None = None
    current_chunk_tokens = 0
    chunk_index = 0

    for para_text, section in paragraphs:
        para_tokens = count_tokens(para_text)
        if para_tokens == 0:
            continue

        if current_chunk_section is None and section:
            current_chunk_section = section

        # If adding this paragraph exceeds target size and we already have content
        if current_chunk_tokens + para_tokens > target_tokens and current_chunk_parts:
            chunk_str = "\n\n".join(current_chunk_parts)
            chunks.append(
                DocumentChunk(
                    chunk_index=chunk_index,
                    text=chunk_str,
                    token_count=current_chunk_tokens,
                    section=current_chunk_section,
                )
            )
            chunk_index += 1

            # Prepare overlap
            overlap_parts: list[str] = []
            overlap_count = 0
            for part in reversed(current_chunk_parts):
                part_toks = count_tokens(part)
                if overlap_count + part_toks <= overlap_tokens:
                    overlap_parts.insert(0, part)
                    overlap_count += part_toks
                else:
                    break

            current_chunk_parts = list(overlap_parts)
            current_chunk_tokens = overlap_count
            current_chunk_section = section

        current_chunk_parts.append(para_text)
        current_chunk_tokens += para_tokens
        if section:
            current_chunk_section = section

    if current_chunk_parts:
        chunk_str = "\n\n".join(current_chunk_parts)
        chunks.append(
            DocumentChunk(
                chunk_index=chunk_index,
                text=chunk_str,
                token_count=current_chunk_tokens,
                section=current_chunk_section,
            )
        )

    return chunks

