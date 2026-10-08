import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Production Incident Investigator",
    page_icon="🚨",
    layout="wide",
)


# -----------------------------
# Helper Functions
# -----------------------------

def show_evidence(evidence_list):
    if not evidence_list:
        st.info("No conflicting evidence found.")
        return

    for index, item in enumerate(evidence_list, start=1):
        source = item.get("source", "Unknown source")
        evidence = item.get("evidence", "")
        relevance = item.get("relevance", "")

        with st.container(border=True):
            st.markdown(f"**Evidence {index} — `{source}`**")
            st.markdown(f"> {evidence}")

            if relevance:
                st.caption(f"Why it matters: {relevance}")


def show_confidence(confidence):
    percentage = int(confidence * 100)

    st.progress(
        min(max(confidence, 0.0), 1.0),
        text=f"Confidence: {percentage}%",
    )


# -----------------------------
# Header
# -----------------------------

st.title("🚨 AI Production Incident Investigator")

st.markdown(
    """
    **RAG + LangGraph + LLM powered production incident analysis**

    Investigate production incidents using logs, system documentation,
    and historical incidents to identify evidence-backed root causes.
    """
)

st.divider()


# -----------------------------
# Incident Input
# -----------------------------

st.subheader("Describe the Production Incident")

incident = st.text_area(
    "Incident description",
    placeholder=(
        "Example: Payment requests are timing out with HTTP 504 "
        "errors and the payment service is reporting database "
        "connection failures."
    ),
    height=140,
)

investigate_button = st.button(
    "🔍 Investigate Incident",
    type="primary",
    use_container_width=True,
)


# -----------------------------
# Investigation
# -----------------------------

if investigate_button:

    if not incident.strip():
        st.warning("Please describe the production incident first.")
        st.stop()

    with st.spinner(
        "Investigating incident using RAG + LangGraph..."
    ):
        try:
            response = requests.post(
                f"{API_URL}/investigate",
                json={"incident": incident},
                timeout=180,
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Could not connect to the FastAPI backend.\n\n"
                "Make sure the backend is running on port 8000."
            )
            st.stop()

        except requests.exceptions.Timeout:
            st.error(
                "❌ Investigation timed out. "
                "The LLM investigation took too long."
            )
            st.stop()

        except requests.exceptions.RequestException as exc:
            st.error(f"❌ Request failed: {exc}")
            st.stop()

    if response.status_code != 200:
        try:
            error_detail = response.json().get(
                "detail",
                "Unknown API error",
            )
        except Exception:
            error_detail = response.text

        st.error(
            f"❌ Investigation failed\n\n"
            f"{error_detail}"
        )
        st.stop()

    data = response.json()

    analysis = data.get("analysis", {})
    hypothesis = data.get("hypothesis", {})
    investigation = data.get("investigation", {})
    result = data.get("result", {})

    st.success("✅ Investigation completed successfully!")

    st.divider()


    # =========================================================
    # INCIDENT ANALYSIS
    # =========================================================

    st.header("📋 Incident Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Service",
            analysis.get(
                "affected_service",
                "Unknown",
            ),
        )

    with col2:
        st.metric(
            "Severity",
            analysis.get(
                "severity",
                "Unknown",
            ),
        )

    with col3:
        st.metric(
            "Incident Type",
            analysis.get(
                "incident_type",
                "Unknown",
            ),
        )


    # -----------------------------
    # Symptoms
    # -----------------------------

    st.subheader("🔎 Observed Symptoms")

    symptoms = analysis.get("symptoms", [])

    if symptoms:
        for symptom in symptoms:
            st.markdown(f"- {symptom}")
    else:
        st.info("No symptoms identified.")


    # -----------------------------
    # Possible Causes
    # -----------------------------

    st.subheader("💭 Possible Causes")

    possible_causes = analysis.get(
        "possible_causes",
        [],
    )

    if possible_causes:
        for index, cause in enumerate(
            possible_causes,
            start=1,
        ):
            st.markdown(
                f"**{index}.** {cause}"
            )
    else:
        st.info("No possible causes identified.")


    st.divider()


    # =========================================================
    # INVESTIGATION HYPOTHESIS
    # =========================================================

    st.header("🧠 Investigation Hypothesis")

    with st.container(border=True):

        st.markdown(
            f"### {hypothesis.get('hypothesis', 'No hypothesis generated')}"
        )

        reasoning = hypothesis.get(
            "reasoning",
            "",
        )

        if reasoning:
            st.markdown("**Reasoning**")
            st.write(reasoning)


    # -----------------------------
    # Evidence Needed
    # -----------------------------

    evidence_needed = hypothesis.get(
        "evidence_needed",
        [],
    )

    if evidence_needed:

        st.subheader("🔬 Evidence Used to Verify the Hypothesis")

        for index, evidence in enumerate(
            evidence_needed,
            start=1,
        ):
            st.markdown(
                f"**{index}.** {evidence}"
            )


    st.divider()


    # =========================================================
    # EVIDENCE EVALUATION
    # =========================================================

    st.header("📊 Evidence Evaluation")

    confidence = investigation.get(
        "confidence",
        0,
    )

    supported = investigation.get(
        "supported",
        False,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Evidence Confidence")
        show_confidence(confidence)

    with col2:

        st.markdown("### Hypothesis Status")

        if supported:
            st.success("✅ SUPPORTED")
        else:
            st.warning("⚠️ NOT SUFFICIENTLY SUPPORTED")


    explanation = investigation.get(
        "explanation",
        "",
    )

    if explanation:

        st.subheader("📝 Investigation Summary")

        with st.container(border=True):
            st.write(explanation)


    # -----------------------------
    # Supporting Evidence
    # -----------------------------

    supporting_evidence = investigation.get(
        "supporting_evidence",
        [],
    )

    st.subheader("✅ Supporting Evidence")

    show_evidence(supporting_evidence)


    # -----------------------------
    # Conflicting Evidence
    # -----------------------------

    conflicting_evidence = investigation.get(
        "conflicting_evidence",
        [],
    )

    st.subheader("⚠️ Conflicting Evidence")

    if conflicting_evidence:
        show_evidence(conflicting_evidence)
    else:
        st.success(
            "No significant conflicting evidence was identified."
        )


    st.divider()


    # =========================================================
    # FINAL ROOT CAUSE
    # =========================================================

    st.header("🎯 Root Cause")

    root_cause = result.get(
        "root_cause",
        "Root cause could not be determined.",
    )

    with st.container(border=True):

        st.markdown(
            f"### {root_cause}"
        )

        final_confidence = result.get(
            "confidence",
            confidence,
        )

        show_confidence(final_confidence)


    st.divider()


    # =========================================================
    # RECOMMENDED FIX
    # =========================================================

    st.header("🛠️ Recommended Fix")

    recommended_fix = result.get(
        "recommended_fix",
        "No remediation recommendation generated.",
    )

    with st.container(border=True):
        st.write(recommended_fix)



    # =========================================================
# DEBUG DATA
# =========================================================

st.divider()

with st.expander("🧪 Developer / Debug Data"):
    st.caption(
        "Raw API response for debugging purposes."
    )

    st.code(
        response.text,
        language="json",
    )