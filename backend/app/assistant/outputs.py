"""Typed outputs and dependency structures for the Document Copilot assistant."""

from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel, Field

from app.retrieval.retriever import DocumentRetriever


class SourcePassage(BaseModel):
    chunk_id: int
    document_id: int
    ticker: str
    company: str
    filing_type: str
    filing_date: str
    fiscal_year: int
    page: str | None = None
    section: str | None = None
    text: str


class Citation(BaseModel):
    chunk_id: int
    company: str
    filing_type: str
    filing_date: str
    page: str | None = None
    section: str | None = None
    excerpt: str = Field(description="Exact or near-verbatim quote from the cited chunk")


class GroundedAnswer(BaseModel):
    answer: str = Field(description="Comprehensive synthesis answering the user's question")
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of all citations supporting factual claims in the answer",
    )
    insufficient_evidence: bool = Field(
        default=False,
        description="True if the corpus context lacked sufficient evidence to answer",
    )


@dataclass
class DocumentAgentDeps:
    user_id: str
    thread_id: int
    retriever: DocumentRetriever
    retrieved_passages: list[dict[str, Any]]

