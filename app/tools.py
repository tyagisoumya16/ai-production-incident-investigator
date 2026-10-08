from app.rag import search_knowledge_base


def search_logs(query: str, k: int = 5) -> list[dict]:
    results = search_knowledge_base(
        f"production logs {query}",
        k=k,
    )

    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "type": doc.metadata.get("type", "unknown"),
            "content": doc.page_content,
        }
        for doc in results
        if doc.metadata.get("type") == "logs"
    ]


def search_documentation(query: str, k: int = 5) -> list[dict]:
    results = search_knowledge_base(
        f"system documentation {query}",
        k=k,
    )

    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "type": doc.metadata.get("type", "unknown"),
            "content": doc.page_content,
        }
        for doc in results
        if doc.metadata.get("type") == "documentation"
    ]


def search_past_incidents(query: str, k: int = 5) -> list[dict]:
    results = search_knowledge_base(
        f"past incidents {query}",
        k=k,
    )

    return [
        {
            "source": doc.metadata.get("source", "unknown"),
            "type": doc.metadata.get("type", "unknown"),
            "content": doc.page_content,
        }
        for doc in results
        if doc.metadata.get("type") == "past_incident"
    ]


def collect_evidence(query: str) -> dict:
    return {
        "logs": search_logs(query),
        "documentation": search_documentation(query),
        "past_incidents": search_past_incidents(query),
    }