from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.llm import get_llm
from app.rag import retrieve_context
from app.schemas import (
    IncidentAnalysis,
    Hypothesis,
    EvidenceEvaluation,
    InvestigationResult,
)
from app.tools import collect_evidence


class InvestigationState(TypedDict, total=False):
    incident: str
    analysis: IncidentAnalysis
    hypothesis: Hypothesis
    evidence: dict
    evaluation: EvidenceEvaluation
    result: InvestigationResult
    attempts: int


def analyze_node(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        IncidentAnalysis,
        method="json_schema",
    )

    context = retrieve_context(
        state["incident"],
        k=6,
    )

    prompt = f"""
You are a production incident investigator.

Analyze this production incident.

Incident:
{state["incident"]}

Retrieved evidence:
{context}

Rules:
- Do not invent facts.
- Identify only observable symptoms.
- Possible causes are hypotheses, not confirmed root causes.
"""

    analysis = structured_llm.invoke(prompt)

    return {
        "analysis": analysis,
    }


def hypothesis_node(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        Hypothesis,
        method="json_schema",
    )

    prompt = f"""
Generate the strongest candidate root-cause hypothesis.

Incident:
{state["incident"]}

Incident analysis:
{state["analysis"].model_dump_json()}

Rules:
- This is NOT confirmed yet.
- Use only facts from the analysis.
- Explain why it is plausible.
- List evidence needed to verify it.
"""

    hypothesis = structured_llm.invoke(prompt)

    return {
        "hypothesis": hypothesis,
    }


def evidence_node(state: InvestigationState):
    query = (
        f"{state['incident']} "
        f"{state['hypothesis'].hypothesis} "
        f"{state['hypothesis'].reasoning}"
    )

    evidence = collect_evidence(query)

    return {
        "evidence": evidence,
    }


def evaluate_node(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        EvidenceEvaluation,
        method="json_schema",
    )

    prompt = f"""
Evaluate the hypothesis using the collected evidence.

Incident:
{state["incident"]}

Hypothesis:
{state["hypothesis"].model_dump_json()}

Collected evidence:
{state["evidence"]}

Determine:

1. Whether the evidence supports the hypothesis.
2. Confidence from 0 to 1.
3. Supporting evidence.
4. Conflicting evidence.
5. Explanation.

Rules:
- Do not invent evidence.
- If evidence conflicts, explicitly mention it.
"""

    evaluation = structured_llm.invoke(prompt)

    return {
        "evaluation": evaluation,
        "attempts": state.get("attempts", 0) + 1,
    }


def route_after_evaluation(state: InvestigationState):
    evaluation = state["evaluation"]

    if (
        evaluation.supported
        and evaluation.confidence >= 0.75
    ):
        return "finalize"

    if state.get("attempts", 0) >= 2:
        return "finalize"

    return "reinvestigate"


def reinvestigate_node(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        Hypothesis,
        method="json_schema",
    )

    prompt = f"""
The previous hypothesis was not sufficiently verified.

Create a better hypothesis based on conflicting or
weak evidence.

Incident:
{state["incident"]}

Previous hypothesis:
{state["hypothesis"].model_dump_json()}

Previous evaluation:
{state["evaluation"].model_dump_json()}

New hypothesis must:
- address the weak/conflicting evidence
- remain testable
- not claim certainty
"""

    hypothesis = structured_llm.invoke(prompt)

    return {
        "hypothesis": hypothesis,
    }


def finalize_node(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        InvestigationResult,
        method="json_schema",
    )

    prompt = f"""
Produce the final production incident investigation.

Incident:
{state["incident"]}

Analysis:
{state["analysis"].model_dump_json()}

Hypothesis:
{state["hypothesis"].model_dump_json()}

Evidence:
{state["evidence"]}

Evaluation:
{state["evaluation"].model_dump_json()}

Rules:
- Root cause must be based on evidence.
- Never invent evidence.
- Confidence must reflect evidence strength.
- Include supporting evidence.
- Include conflicting evidence if present.
- Recommend a practical engineering fix.
"""

    result = structured_llm.invoke(prompt)

    return {
        "result": result,
    }


def build_graph():
    graph = StateGraph(InvestigationState)

    graph.add_node("analyze", analyze_node)
    graph.add_node("hypothesis", hypothesis_node)
    graph.add_node("evidence", evidence_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("reinvestigate", reinvestigate_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "hypothesis")
    graph.add_edge("hypothesis", "evidence")
    graph.add_edge("evidence", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "finalize": "finalize",
            "reinvestigate": "reinvestigate",
        },
    )

    graph.add_edge(
        "reinvestigate",
        "evidence",
    )

    graph.add_edge(
        "finalize",
        END,
    )

    return graph.compile()