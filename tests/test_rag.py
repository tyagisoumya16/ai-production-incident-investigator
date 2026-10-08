from app.rag import search_knowledge_base


def test_rag_search():
    results = search_knowledge_base(
        "database connection pool exhaustion",
        k=3,
    )

    assert len(results) > 0

    text = " ".join(
        result.page_content.lower()
        for result in results
    )

    assert (
        "database" in text
        or "connection" in text
        or "pool" in text
    )