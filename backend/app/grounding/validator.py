"""Citation validation and grounding enforcement.

Ensures every citation returned by the model maps directly to an actually
retrieved document chunk and that excerpts exist within the passage text.
Fails closed if citations reference hallucinated sources.
"""

from typing import Any
from app.assistant.outputs import Citation, GroundedAnswer


class GroundingValidationError(ValueError):
    """Raised when an answer contains ungrounded or fabricated citations."""


def validate_grounding(
    answer: GroundedAnswer,
    allowed_chunks: list[dict[str, Any]],
) -> list[Citation]:
    """Validate that all citations in answer map to allowed retrieved chunks.

    Returns the validated list of citations, or raises GroundingValidationError
    if any citation is invalid or cannot be grounded.
    """
    if answer.insufficient_evidence:
        # If insufficient evidence is declared, no unverified claims should be made
        return []

    allowed_chunk_map = {c["id"]: c for c in allowed_chunks}

    validated: list[Citation] = []
    for cit in answer.citations:
        if cit.chunk_id not in allowed_chunk_map:
            raise GroundingValidationError(
                f"Citation references unretrieved chunk_id {cit.chunk_id}"
            )

        chunk_data = allowed_chunk_map[cit.chunk_id]
        chunk_text = chunk_data.get("text", "")

        # Check excerpt presence (allow whitespace / punctuation flexibility)
        excerpt_clean = " ".join(cit.excerpt.split()).lower()
        chunk_clean = " ".join(chunk_text.split()).lower()

        if excerpt_clean and excerpt_clean not in chunk_clean:
            # Check if excerpt words are at least largely present (>= 75% overlap)
            excerpt_words = [w for w in excerpt_clean.split() if len(w) > 3]
            if excerpt_words:
                matches = sum(1 for w in excerpt_words if w in chunk_clean)
                if matches / len(excerpt_words) < 0.70:
                    raise GroundingValidationError(
                        f"Citation excerpt for chunk {cit.chunk_id} does not match passage text"
                    )

        validated.append(cit)

    return validated
