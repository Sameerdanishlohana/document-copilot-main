"""Corpus ingestion pipeline.

Reads normalized Markdown files and filing metadata from manifest.json,
chunks the filings, generates OpenAI embeddings in batches, and writes
source_documents and document_chunks to Supabase (idempotently).
"""

import json
from pathlib import Path
import sys
import time

from openai import OpenAI

from app.config import settings
from app.database.supabase import get_service_role_client
from ingest.chunker import chunk_markdown

TICKER_TO_COMPANY = {
    "AAPL": "Apple Inc.",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
}


def get_existing_accession_numbers(client) -> set[str]:
    """Retrieve all accession numbers already stored in source_documents."""
    response = client.table("source_documents").select("accession_number").execute()
    return {row["accession_number"] for row in (response.data or [])}


def generate_embeddings_batch(
    openai_client: OpenAI, texts: list[str], model: str = settings.openai_embedding_model, max_retries: int = 3
) -> list[list[float]]:
    """Generate embeddings for a list of texts in a single batch call with retry."""
    if not texts:
        return []
    cleaned_texts = [t.replace("\r\n", " ").replace("\n", " ") for t in texts]
    for attempt in range(1, max_retries + 1):
        try:
            response = openai_client.embeddings.create(input=cleaned_texts, model=model)
            return [item.embedding for item in response.data]
        except Exception as err:
            if attempt == max_retries:
                raise
            print(f"      [Retry {attempt}/{max_retries}] Embedding error: {err}. Retrying in 2s...")
            time.sleep(2)


def insert_chunks_with_retry(supabase_client, chunk_rows: list[dict], max_retries: int = 3) -> None:
    """Insert chunk batch into Supabase with automatic retry on network disconnects."""
    for attempt in range(1, max_retries + 1):
        try:
            supabase_client.table("document_chunks").insert(chunk_rows).execute()
            return
        except Exception as err:
            if attempt == max_retries:
                raise
            print(f"      [Retry {attempt}/{max_retries}] DB insert error: {err}. Retrying in 2s...")
            time.sleep(2)


def ingest_corpus(
    manifest_path: Path,
    markdown_dir: Path,
    limit: int | None = None,
    batch_size: int = 64,
) -> None:
    if not manifest_path.exists():
        print(f"Error: Manifest file {manifest_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    filings = manifest_data.get("filings", [])
    if limit:
        filings = filings[:limit]

    print(f"Total filings to process: {len(filings)}")

    supabase = get_service_role_client()
    openai_client = OpenAI(
        api_key=settings.effective_api_key,
        base_url=settings.effective_base_url,
    )

    existing_accessions = get_existing_accession_numbers(supabase)
    print(f"Already ingested accession numbers: {len(existing_accessions)}")

    total_chunks_written = 0

    for idx, filing in enumerate(filings, 1):
        accession = filing["accession_number"]
        ticker = filing["ticker"]
        filing_date = filing["filing_date"]
        source_url = filing["source_url"]
        company = TICKER_TO_COMPANY.get(ticker, ticker)

        # local_path in manifest is e.g. "2025\\aapl_10-k_2025-10-31_0000320193-25-000079.htm"
        local_rel = Path(filing["local_path"])
        fiscal_year = int(local_rel.parts[0])
        md_filename = local_rel.with_suffix(".md")
        md_file_path = markdown_dir / md_filename

        print(f"\n[{idx}/{len(filings)}] Filing {ticker} {fiscal_year} ({accession})")

        if accession in existing_accessions:
            print(f"  ⏭ Already ingested. Skipping.")
            continue

        if not md_file_path.exists():
            print(f"  ✗ Markdown file not found: {md_file_path}", file=sys.stderr)
            continue

        markdown_content = md_file_path.read_text(encoding="utf-8")

        # 1. Write source_document row
        doc_payload = {
            "ticker": ticker,
            "company": company,
            "filing_type": filing.get("form", "10-K"),
            "fiscal_year": fiscal_year,
            "filing_date": filing_date,
            "accession_number": accession,
            "source_url": source_url,
            "content": markdown_content,
        }

        doc_res = supabase.table("source_documents").insert(doc_payload).execute()
        if not doc_res.data:
            print(f"  ✗ Failed to insert source_document for {accession}", file=sys.stderr)
            continue

        doc_id = doc_res.data[0]["id"]
        print(f"  ✓ Created source_document (id={doc_id})")

        # 2. Chunk markdown
        t0 = time.time()
        chunks = chunk_markdown(markdown_content, target_tokens=600, overlap_tokens=100)
        print(f"  Parsed {len(chunks)} chunks in {time.time() - t0:.2f}s")

        if not chunks:
            continue

        # 3. Generate embeddings & insert in batches
        t_embed = time.time()
        for b_start in range(0, len(chunks), batch_size):
            b_chunks = chunks[b_start : b_start + batch_size]
            b_texts = [c.text for c in b_chunks]

            embeddings = generate_embeddings_batch(
                openai_client, b_texts, model=settings.openai_embedding_model
            )

            chunk_rows = []
            for c, emb in zip(b_chunks, embeddings):
                meta_json = {
                    "ticker": ticker,
                    "company": company,
                    "filing_type": filing.get("form", "10-K"),
                    "filing_date": filing_date,
                    "fiscal_year": fiscal_year,
                    "accession_number": accession,
                    "page": c.page,
                    "section": c.section,
                }
                chunk_rows.append(
                    {
                        "document_id": doc_id,
                        "chunk_index": c.chunk_index,
                        "page": c.page,
                        "section": c.section,
                        "text": c.text,
                        "token_count": c.token_count,
                        "embedding": emb,
                        "metadata": meta_json,
                    }
                )

            # Insert batch into Supabase
            insert_chunks_with_retry(supabase, chunk_rows)
            total_chunks_written += len(chunk_rows)
            print(f"    Uploaded chunks {b_start + 1}-{b_start + len(b_chunks)} of {len(chunks)}")

        print(f"  ✓ Finished embedding and writing {len(chunks)} chunks in {time.time() - t_embed:.2f}s")
        existing_accessions.add(accession)

    print(f"\n==========================================")
    print(f"Ingestion complete! Total chunks inserted: {total_chunks_written}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    manifest = base_dir / "data" / "downloads" / "manifest.json"
    markdown_path = base_dir / "data" / "markdown"

    # Optional CLI argument for limiting filings during test runs
    limit_arg = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit_arg = int(sys.argv[1])

    ingest_corpus(manifest, markdown_path, limit=limit_arg)

