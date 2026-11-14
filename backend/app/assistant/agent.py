"""Agent definition for Document Copilot using PydanticAI."""

from pathlib import Path
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.assistant.outputs import DocumentAgentDeps, GroundedAnswer
from app.config import settings

_INSTRUCTIONS_PATH = Path(__file__).resolve().parent / "instructions.md"
SYSTEM_INSTRUCTIONS = _INSTRUCTIONS_PATH.read_text(encoding="utf-8")

# Configure provider with OpenRouter credentials
client = AsyncOpenAI(
    api_key=settings.effective_api_key,
    base_url=settings.effective_base_url,
)
provider = OpenAIProvider(openai_client=client)
ai_model = OpenAIChatModel(settings.openai_chat_model, provider=provider)

document_agent = Agent(
    model=ai_model,
    deps_type=DocumentAgentDeps,
    output_type=GroundedAnswer,
    system_prompt=SYSTEM_INSTRUCTIONS,
    retries=3,
)


@document_agent.tool
def get_retrieved_passages(ctx: RunContext[DocumentAgentDeps]) -> list[dict]:
    """Retrieve the top pre-fetched relevant 10-K passages with their chunk_id, section, and text."""
    return [
        {
            "chunk_id": p.get("id"),
            "ticker": p.get("metadata", {}).get("ticker"),
            "company": p.get("metadata", {}).get("company"),
            "filing_type": p.get("metadata", {}).get("filing_type"),
            "filing_date": p.get("metadata", {}).get("filing_date"),
            "fiscal_year": p.get("metadata", {}).get("fiscal_year"),
            "page": p.get("page"),
            "section": p.get("section"),
            "text": p.get("text"),
        }
        for p in ctx.deps.retrieved_passages
    ]


@document_agent.tool
def search_filings(
    ctx: RunContext[DocumentAgentDeps],
    query: str,
    ticker: str | None = None,
    fiscal_year: int | None = None,
) -> list[dict]:
    """Search the SEC filing corpus for additional passages matching the query."""
    results = ctx.deps.retriever.search(
        query=query,
        ticker=ticker,
        fiscal_year=fiscal_year,
        top_k=5,
    )
    # Register any new passages into the dependency's retrieved set for grounding validation
    existing_ids = {p["id"] for p in ctx.deps.retrieved_passages}
    for r in results:
        if r["id"] not in existing_ids:
            ctx.deps.retrieved_passages.append(r)
            existing_ids.add(r["id"])

    return [
        {
            "chunk_id": r.get("id"),
            "ticker": r.get("metadata", {}).get("ticker"),
            "company": r.get("metadata", {}).get("company"),
            "filing_date": r.get("metadata", {}).get("filing_date"),
            "section": r.get("section"),
            "text": r.get("text"),
        }
        for r in results
    ]


@document_agent.tool
def read_surrounding_chunks(ctx: RunContext[DocumentAgentDeps], chunk_id: int) -> list[dict]:
    """Inspect the neighboring chunks before and after a specific chunk for broader context."""
    for p in ctx.deps.retrieved_passages:
        if p.get("id") == chunk_id:
            neighbors = p.get("neighbors", [])
            for n in neighbors:
                if n["id"] not in {x["id"] for x in ctx.deps.retrieved_passages}:
                    ctx.deps.retrieved_passages.append(n)
            return [
                {
                    "chunk_id": n.get("id"),
                    "chunk_index": n.get("chunk_index"),
                    "text": n.get("text"),
                }
                for n in neighbors
            ]
    return []

