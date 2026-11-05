import logging
from typing import Literal

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.agents.learning_agent import LearningAgent
from backend.rag.query import answer_pdf, ingest_pdf
from backend.agents.tracker_agent import add_progress, list_progress
from backend.orchestrator import run_assistant

logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Personal AI Assistant")
assistant = LearningAgent()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=20000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    agent: Literal["auto", "learning", "interview", "planner"] = "learning"
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
    )


class PDFQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    document_id: str = Field(pattern=r"^[a-f0-9]{64}$")

class ProgressRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    notes: str = Field(default="", max_length=5000)

@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat")
def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        raise HTTPException(400, "Please enter a question.")

    try:
        return run_assistant(
            question,
            request.agent,
            [message.model_dump() for message in request.history],
        )

    except requests.RequestException:
        logger.exception("Chat request failed")
        raise HTTPException(
            503,
            "Cannot get an answer from Ollama. Check that "
            "Ollama is running and the model is downloaded.",
        )

@app.post("/documents")
def upload_document(file: UploadFile = File(...)):
    try:
        filename = file.filename or ""

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a PDF file.",
            )

        max_size = 10 * 1024 * 1024
        content = file.file.read(max_size + 1)

        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="PDF must be 10 MB or smaller.",
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="This file is not a valid PDF.",
            )

        return ingest_pdf(content, filename)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        logger.exception("PDF indexing failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Indexing failed. Check Ollama, nomic-embed-text, "
                "and the backend terminal."
            ),
        )

    finally:
        file.file.close()


@app.post("/documents/ask")
def ask_document(request: PDFQuestion):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    try:
        return answer_pdf(question, request.document_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        logger.exception("PDF question failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Document Q&A failed. Check Ollama "
                "and the backend terminal."
            ),
        )
@app.post("/progress")
def save_progress(request: ProgressRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(400, "Please enter a topic.")

    return add_progress(topic, request.notes.strip())


@app.get("/progress")
def get_progress():
    return {"items": list_progress()}