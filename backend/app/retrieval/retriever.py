"""Retriever service for hybrid document search (vector + BM25 full-text + RRF)."""

from typing import Any
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.retrieval.fusion import fuse_search_results
from app.retrieval.queries import get_neighbor_chunks, query_full_text, query_semantic


class DocumentRetriever:
    """Orchestrates hybrid retrieval over ingested SEC filings."""

    def __init__(
        self,
        openai_client: OpenAI | None = None,
        db_session_factory: sessionmaker[Session] | None = None,
    ):
        self.openai_client = openai_client or OpenAI(
            api_key=settings.effective_api_key,
            base_url=settings.effective_base_url,
        )
        if db_session_factory is None:
            engine = create_engine(settings.sqlalchemy_database_url, pool_pre_ping=True)
            self.session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        else:
            self.session_factory = db_session_factory

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding vector for search query."""
        cleaned = query.replace("\r\n", " ").replace("\n", " ").strip()
        res = self.openai_client.embeddings.create(
            input=[cleaned],
            model=settings.openai_embedding_model,
        )
        return res.data[0].embedding

    def search(
        self,
        query: str,
        ticker: str | None = None,
        fiscal_year: int | None = None,
        candidate_k: int = settings.retrieval_candidate_k,
        top_k: int = settings.retrieval_top_k,
        rrf_k: int = settings.retrieval_rrf_k,
        neighbor_radius: int = settings.retrieval_neighbor_radius,
    ) -> list[dict[str, Any]]:
        """Run hybrid search, fuse with RRF, and attach neighbor context."""
        query_embedding = self.embed_query(query)

        with self.session_factory() as session:
            # 1. Semantic search
            vector_results = query_semantic(
                session=session,
                query_embedding=query_embedding,
                limit=candidate_k,
                ticker=ticker,
                fiscal_year=fiscal_year,
            )

            # 2. Lexical search
            fts_results = query_full_text(
                session=session,
                query_text=query,
                limit=candidate_k,
                ticker=ticker,
                fiscal_year=fiscal_year,
                fts_config=settings.retrieval_fts_config,
            )

            # 3. Reciprocal Rank Fusion
            fused = fuse_search_results(
                vector_results=vector_results,
                fts_results=fts_results,
                k=rrf_k,
            )

            top_results = fused[:top_k]

            # 4. Attach surrounding neighbor chunks
            for item in top_results:
                neighbors = get_neighbor_chunks(
                    session=session,
                    document_id=item["document_id"],
                    chunk_index=item["chunk_index"],
                    radius=neighbor_radius,
                )
                item["neighbors"] = neighbors

            return top_results

