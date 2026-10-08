from langchain_groq import ChatGroq

from app.config import settings


def get_llm():
    if settings.llm_provider.lower() != "groq":
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is missing")

    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        temperature=0,
    )