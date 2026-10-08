from app.llm import get_llm
from app.rag import retrieve_context
from app.schemas import Hypothesis


def generate_hypotheses(
    incident: str,
) -> list[Hypothesis]:

    context = retrieve_context(
        query=incident,
        k=8,
    )

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        Hypothesis,
        method="json_schema",
    )
    
    prompt = f"""
You are a production incident investigator.

Generate ONE strong candidate hypothesis for the
incident based only on the evidence.

Incident:
{incident}

Evidence:
{context}

Rules:
- Do not invent evidence.
- Do not call the hypothesis a confirmed root cause.
- Explain why this hypothesis is plausible.
- List exactly what evidence should be checked to verify it.
"""

    hypothesis = structured_llm.invoke(prompt)

    return [hypothesis]