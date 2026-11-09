from ingest.chunker import chunk_markdown, count_tokens


def test_count_tokens():
    tokens = count_tokens("Hello world")
    assert tokens > 0


def test_chunk_markdown_empty():
    assert chunk_markdown("") == []
    assert chunk_markdown("   ") == []


def test_chunk_markdown_simple():
    text = """# Item 1. Business

Apple designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories.

# Item 1A. Risk Factors

The Company's business, reputation, results of operations and financial condition can be affected by adverse economic conditions.
"""
    chunks = chunk_markdown(text, target_tokens=30, overlap_tokens=10)
    assert len(chunks) >= 1
    assert all(c.token_count > 0 for c in chunks)
    assert chunks[0].chunk_index == 0
