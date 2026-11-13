"""Unit tests for citation grounding validator."""

import pytest
from app.assistant.outputs import Citation, GroundedAnswer
from app.grounding.validator import GroundingValidationError, validate_grounding


def test_valid_citation_passes():
    allowed = [
        {"id": 1, "text": "Apple Net Sales for iPhone was $201 billion in fiscal year 2024."}
    ]
    citation = Citation(
        chunk_id=1,
        company="Apple Inc.",
        filing_type="10-K",
        filing_date="2024-11-01",
        page="32",
        section="Item 7",
        excerpt="iPhone was $201 billion in fiscal year 2024",
    )
    answer = GroundedAnswer(
        answer="iPhone net sales reached $201 billion in 2024.",
        citations=[citation],
        insufficient_evidence=False,
    )
    validated = validate_grounding(answer, allowed)
    assert len(validated) == 1
    assert validated[0].chunk_id == 1


def test_unretrieved_chunk_raises_error():
    allowed = [{"id": 1, "text": "Some text"}]
    citation = Citation(
        chunk_id=999,  # Not in allowed chunks
        company="Apple Inc.",
        filing_type="10-K",
        filing_date="2024-11-01",
        excerpt="Some text",
    )
    answer = GroundedAnswer(
        answer="Fabricated fact",
        citations=[citation],
        insufficient_evidence=False,
    )
    with pytest.raises(GroundingValidationError) as exc:
        validate_grounding(answer, allowed)
    assert "unretrieved chunk_id 999" in str(exc.value)


def test_hallucinated_excerpt_raises_error():
    allowed = [{"id": 1, "text": "Microsoft Azure cloud revenue expanded significantly."}]
    citation = Citation(
        chunk_id=1,
        company="Microsoft",
        filing_type="10-K",
        filing_date="2024-07-30",
        excerpt="Tesla delivered 1 million electric vehicles globally",  # Completely ungrounded excerpt
    )
    answer = GroundedAnswer(
        answer="Tesla delivery claims",
        citations=[citation],
        insufficient_evidence=False,
    )
    with pytest.raises(GroundingValidationError) as exc:
        validate_grounding(answer, allowed)
    assert "does not match passage text" in str(exc.value)
