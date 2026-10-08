from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    incident: str = Field(min_length=10)


class Evidence(BaseModel):
    source: str
    evidence: str
    relevance: str


class IncidentAnalysis(BaseModel):
    incident_type: str
    affected_service: str
    severity: str
    symptoms: list[str]
    possible_causes: list[str]


class Hypothesis(BaseModel):
    hypothesis: str
    reasoning: str
    evidence_needed: list[str]


class EvidenceEvaluation(BaseModel):
    supported: bool
    confidence: float = Field(ge=0, le=1)
    supporting_evidence: list[Evidence]
    conflicting_evidence: list[Evidence]
    explanation: str


class InvestigationResult(BaseModel):
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    supporting_evidence: list[Evidence]
    conflicting_evidence: list[Evidence]
    recommended_fix: str


class IncidentResponse(BaseModel):
    incident: str
    analysis: IncidentAnalysis
    hypothesis: Hypothesis
    investigation: EvidenceEvaluation
    result: InvestigationResult