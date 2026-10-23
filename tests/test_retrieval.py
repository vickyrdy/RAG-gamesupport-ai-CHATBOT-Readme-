import pytest
from app.retrieval import retrieve


@pytest.mark.parametrize("question,expected_source", [
    ("What is the refund policy?", "refund-policy.md"),
    ("How do I reset my password?", "password-reset.md"),
    ("My payment failed. What should I do?", "payment-failures.md"),
    ("My purchase is missing.", "missing-purchases.md"),
    ("The game keeps crashing.", "crashes.md"),
    ("Can PC players play with Xbox players?", "cross-platform-play.md"),
])
def test_expected_document_in_top_three(
    question, expected_source
):
    results = retrieve(question, limit=3)
    sources = [result["source"] for result in results]

    assert expected_source in sources, (
        f"Expected {expected_source}, retrieved {sources}"
    )


def test_result_structure():
    results = retrieve("What is the refund policy?", limit=3)

    assert len(results) == 3

    for result in results:
        assert result["text"]
        assert result["source"].endswith(".md")
        assert isinstance(result["score"], (int, float))
        