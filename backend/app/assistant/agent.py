"""Agent definition for Document Copilot using PydanticAI."""

from pathlib import Path
from pydantic_ai import Agent, RunContext

from app.assistant.outputs import DocumentAgentDeps, GroundedAnswer
from app.config import settings

_INSTRUCTIONS_PATH = Path(__file__).resolve().parent / "instructions.md"
SYSTEM_INSTRUCTIONS = _INSTRUCTIONS_PATH.read_text(encoding="utf-8")

document_agent = Agent(
    model=f"openai:{settings.openai_chat_model}",
    deps_type=DocumentAgentDeps,
    output_type=GroundedAnswer,
    system_prompt=SYSTEM_INSTRUCTIONS,
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

