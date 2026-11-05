# Multi-Agent Personal AI Assistant

A local Python application for learning, interview preparation,
study planning, PDF question answering, and progress tracking.

## Features

- Learning, interview, and planning coaches
- Keyword-based coach routing using LangGraph
- Conversation history within the current browser session
- PDF retrieval using LangChain embeddings and ChromaDB
- Retrieved passages with page references
- Persistent progress records using SQLite

## Technology

Python, FastAPI, Streamlit, Ollama, LangGraph,
LangChain, ChromaDB, SQLite, and pypdf.

## Setup on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

Install and start Ollama before using AI features.

## Run backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

## Run frontend in another terminal

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py
```

Frontend: http://localhost:8501
API documentation: http://127.0.0.1:8000/docs

## Limitations 

- Intended for local, single-user use.
- Automatic routing uses keyword rules.
- Chat history is not saved permanently.
- PDF questions use one selected document.
- Scanned PDFs require OCR, which is not implemented.
- Model answers and citations require verification.
- Ollama models must be downloaded separately.