from app.llm import get_llm
from app.rag import retrieve_context
from app.schemas import IncidentAnalysis


def analyze_incident(
    incident: str,
) -> IncidentAnalysis:

    context = retrieve_context(
        query=incident,
        k=6,
    )

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        IncidentAnalysis,
        method="json_schema",
    )

    prompt = f"""
You are a production incident analysis expert.

Analyze the incident using ONLY the provided
incident description and retrieved evidence.

Do not invent facts.

Incident:
{incident}

Retrieved Evidence:
{context}

Determine:

1. Incident type
2. Affected service
3. Severity
4. Observable symptoms
5. Possible causes

Important:
- Possible causes are hypotheses, not confirmed root causes.
- Do not claim a root cause yet.
- Every conclusion must be supported by the evidence.
"""

    result = structured_llm.invoke(prompt)

    return result