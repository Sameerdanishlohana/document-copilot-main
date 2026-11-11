"""SQL queries and execution helpers for vector and full-text search over document_chunks."""

from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session


def query_semantic(
    session: Session,
    query_embedding: list[float],
    limit: int = 50,
    ticker: str | None = None,
    fiscal_year: int | None = None,
) -> list[dict[str, Any]]:
    """Query document_chunks using pgvector cosine distance <=> operator.

    Returns the top-k chunks ordered by cosine similarity descending.
    """
    filters = []
    params: dict[str, Any] = {
        "embedding": str(query_embedding),
        "limit": limit,
    }

    if ticker:
        filters.append("metadata->>'ticker' = :ticker")
        params["ticker"] = ticker
    if fiscal_year:
        filters.append("(metadata->>'fiscal_year')::int = :fiscal_year")
        params["fiscal_year"] = fiscal_year

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = f"""
    SELECT
        id,
        document_id,
        chunk_index,
        page,
        section,
        text,
        token_count,
        metadata,
        1 - (embedding <=> :embedding::vector) AS similarity_score
    FROM document_chunks
    {where_clause}
    ORDER BY embedding <=> :embedding::vector ASC
    LIMIT :limit;
    """

    res = session.execute(text(sql), params)
    rows = []
    for row in res.mappings():
        rows.append(dict(row))
    return rows


def query_full_text(
    session: Session,
    query_text: str,
    limit: int = 50,
    ticker: str | None = None,
    fiscal_year: int | None = None,
    fts_config: str = "english",
) -> list[dict[str, Any]]:
    """Query document_chunks using Postgres full-text search over search_vector.

    Uses websearch_to_tsquery or plainto_tsquery for robust query parsing.
    """
    filters = ["search_vector @@ websearch_to_tsquery(:config, :query)"]
    params: dict[str, Any] = {
        "config": fts_config,
        "query": query_text,
        "limit": limit,
    }

    if ticker:
        filters.append("metadata->>'ticker' = :ticker")
        params["ticker"] = ticker
    if fiscal_year:
        filters.append("(metadata->>'fiscal_year')::int = :fiscal_year")
        params["fiscal_year"] = fiscal_year

    where_clause = "WHERE " + " AND ".join(filters)

    sql = f"""
    SELECT
        id,
        document_id,
        chunk_index,
        page,
        section,
        text,
        token_count,
        metadata,
        ts_rank_cd(search_vector, websearch_to_tsquery(:config, :query)) AS rank_score
    FROM document_chunks
    {where_clause}
    ORDER BY rank_score DESC
    LIMIT :limit;
    """

    res = session.execute(text(sql), params)
    rows = []
    for row in res.mappings():
        rows.append(dict(row))
    return rows


def get_neighbor_chunks(
    session: Session,
    document_id: int,
    chunk_index: int,
    radius: int = 1,
) -> list[dict[str, Any]]:
    """Fetch neighbor chunks surrounding a target chunk for expanded context."""
    sql = """
    SELECT
        id,
        document_id,
        chunk_index,
        page,
        section,
        text,
        token_count,
        metadata
    FROM document_chunks
    WHERE document_id = :document_id
      AND chunk_index BETWEEN :min_idx AND :max_idx
    ORDER BY chunk_index ASC;
    """
    params = {
        "document_id": document_id,
        "min_idx": max(0, chunk_index - radius),
        "max_idx": chunk_index + radius,
    }
    res = session.execute(text(sql), params)
    return [dict(row) for row in res.mappings()]
