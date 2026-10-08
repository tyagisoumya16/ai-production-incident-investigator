import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph import build_graph
from app.rag import retrieve_context
from app.schemas import IncidentRequest


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    ),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI Production Incident Investigator",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


# --------------------------------------------------
# RAG Search
# --------------------------------------------------

@app.post("/rag/search")
def rag_search(request: IncidentRequest):
    try:
        logger.info(
            "RAG search started: %s",
            request.incident,
        )

        context = retrieve_context(
            request.incident,
            k=4,
        )

        return {
            "query": request.incident,
            "context": context,
        }

    except Exception as exc:
        logger.exception("RAG search failed")

        raise HTTPException(
            status_code=500,
            detail=f"RAG search failed: {str(exc)}",
        ) from exc


# --------------------------------------------------
# Incident Investigation
# --------------------------------------------------

@app.post("/investigate")
def investigate(request: IncidentRequest):
    try:
        logger.info(
            "Starting incident investigation"
        )

        graph = build_graph()

        result = graph.invoke(
            {
                "incident": request.incident,
                "attempts": 0,
            }
        )

        logger.info(
            "Incident investigation completed"
        )

        return {
            "incident": request.incident,
            "analysis": result["analysis"].model_dump(),
            "hypothesis": result["hypothesis"].model_dump(),
            "investigation": result["evaluation"].model_dump(),
            "result": result["result"].model_dump(),
        }

    except Exception as exc:
        logger.exception(
            "Incident investigation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Incident investigation failed: {str(exc)}",
        ) from exc