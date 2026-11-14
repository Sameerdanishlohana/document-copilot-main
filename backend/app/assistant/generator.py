"""Agent generation helper for Document Copilot.

Uses typed JSON generation to generate GroundedAnswer models with citations
from retrieved SEC filing passages.
"""

import json
from pathlib import Path
from openai import AsyncOpenAI

from app.assistant.outputs import Citation, GroundedAnswer
from app.config import settings

_INSTRUCTIONS_PATH = Path(__file__).resolve().parent / "instructions.md"
SYSTEM_INSTRUCTIONS = _INSTRUCTIONS_PATH.read_text(encoding="utf-8")


async def generate_grounded_answer(
    query: str,
    passages: list[dict],
) -> GroundedAnswer:
    """Generate a structured, cited answer from retrieved passages."""
    client = AsyncOpenAI(
        api_key=settings.effective_api_key,
        base_url=settings.effective_base_url,
    )

    passages_text = []
    for p in passages:
        meta = p.get("metadata", {})
        ticker = meta.get("ticker", "N/A")
        year = meta.get("fiscal_year", "N/A")
        date_str = meta.get("filing_date", "N/A")
        company = meta.get("company", ticker)
        f_type = meta.get("filing_type", "10-K")
        page = p.get("page") or "N/A"
        section = p.get("section") or "N/A"
        chunk_id = p.get("id")

        header = f"[Chunk ID: {chunk_id}] Company: {company} ({ticker}) | Filing: {f_type} {year} (Date: {date_str}) | Page: {page} | Section: {section}"
        passages_text.append(f"{header}\n{p.get('text', '')}")

    context_block = "\n\n---\n\n".join(passages_text)

    prompt = f"""Based on the following retrieved SEC filing passages, answer the analyst's question.

Retrieved Context:
{context_block}

Question:
{query}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "answer": "Clear synthesis of the findings",
  "citations": [
    {{
      "chunk_id": 123,
      "company": "Company Name",
      "filing_type": "10-K",
      "filing_date": "YYYY-MM-DD",
      "page": "page or null",
      "section": "section or null",
      "excerpt": "Exact quotation from the chunk text"
    }}
  ],
  "insufficient_evidence": false
}}

If the passages do not contain enough evidence to answer, set "insufficient_evidence": true and state that the corpus does not contain enough evidence in "answer".
"""

    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=settings.openai_agent_temperature,
    )

    raw_json = response.choices[0].message.content or "{}"
    data = json.loads(raw_json)

    citations = [
        Citation(
            chunk_id=c.get("chunk_id"),
            company=c.get("company", ""),
            filing_type=c.get("filing_type", "10-K"),
            filing_date=str(c.get("filing_date", "")),
            page=c.get("page"),
            section=c.get("section"),
            excerpt=c.get("excerpt", ""),
        )
        for c in data.get("citations", [])
        if c.get("chunk_id") is not None
    ]

    return GroundedAnswer(
        answer=data.get("answer", ""),
        citations=citations,
        insufficient_evidence=bool(data.get("insufficient_evidence", False)),
    )
