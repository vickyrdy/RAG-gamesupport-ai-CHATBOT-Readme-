# Vaelthryn: Echoes of the Fallen — AI Support Assistant

A multi-turn Retrieval-Augmented Generation (RAG) support assistant for the fictional game **Vaelthryn: Echoes of the Fallen**.

It answers gameplay, account, and policy questions using local Markdown documentation, maintains conversation context, applies basic prompt-injection and secret-leakage guardrails, and includes automated evaluation and CI checks.

## Features

- FastAPI web application with a dark fantasy support-chat frontend
- Multi-turn conversation support using LangGraph
- SQLite-backed conversation checkpoints
- Document retrieval using Qdrant and `sentence-transformers/all-MiniLM-L6-v2`
- Groq-powered LLM responses using `openai/gpt-oss-20b`
- Source citations in responses
- Input blocking and output redaction for selected prompt-injection and API-key patterns
- Offline pytest and unittest suites
- DeepEval-based single-turn, multi-turn, and red-team evaluations
- GitHub Actions workflows for offline tests and manual live evaluations
- Docker packaging with persistent Qdrant and SQLite volumes

## Tech Stack

- Python 3.11
- FastAPI
- LangGraph
- LangChain Groq
- Qdrant
- SQLite
- DeepEval
- Docker / Docker Compose
- GitHub Actions

## Project Structure

```text
app/
  main.py          # FastAPI application and chat endpoint
  agent.py         # LangGraph agent and Groq integration
  retrieval.py     # Qdrant document retrieval
  ingest.py        # Markdown ingestion and indexing
  guardrails.py    # Input/output safety checks
  static/          # Browser frontend
data/
  docs/            # Markdown support documents
evaluation/        # DeepEval and red-team scripts
tests/             # Offline tests
.github/workflows/ # CI workflows
```

## Local Setup

### 1. Create a virtual environment

```powershell
cd D:\RAGG
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Groq

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` or expose API keys.

### 4. Index support documents

```powershell
.\.venv\Scripts\python.exe -m app.ingest
```

This creates or recreates the local Qdrant collection from Markdown files in `data/docs`.

### 5. Run the application

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

## Docker Setup

### Build the image

```powershell
docker build -t gamesupport-ai:latest .
```

### Start the application

```powershell
docker compose up -d
```

Open:

```text
http://localhost:8000
```

### Check health

```powershell
curl.exe http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

### Index documents inside Docker

Run this once after changing documents in `data/docs`:

```powershell
docker compose run --rm api python -m app.ingest
```

This indexes into the Docker Qdrant volume, not the host `.qdrant` folder.

### Restart the container

```powershell
docker compose restart api
```

Conversation state persists in the Docker SQLite volume.

### Stop the application

```powershell
docker compose down
```

Docker volumes remain available for the next start.

## API

### `GET /health`

Returns:

```json
{ "status": "ok" }
```

### `POST /chat`

Request:

```json
{
  "user_id": "user-123",
  "thread_id": "thread-456",
  "message": "How do I reset my password?"
}
```

Response:

```json
{
  "answer": "Use the password-reset option...",
  "sources": ["password-reset.md"],
  "blocked": false
}
```

## Testing

Run offline tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Run guardrail tests:

```powershell
.\.venv\Scripts\python.exe -m unittest evaluation.test_guardrails evaluation.test_api_guardrails -v
```

## Evaluations

The project includes:

- Single-turn faithfulness and answer-relevancy checks
- A two-turn conversation-relevancy smoke test
- Five direct prompt-injection and data-leakage red-team cases
- JSON result reports uploaded as GitHub Actions artifacts

Live evaluations require a valid `GROQ_API_KEY` GitHub repository secret and are run manually through `workflow_dispatch`.

Evaluation results can vary because they use an LLM judge. A failed relevancy score does not automatically mean the answer was incorrect.

## Security Scope

The guardrails provide limited protection against:

- Common instruction-override requests
- System-prompt extraction requests
- Selected synthetic API-key patterns
- Selected secret-like output patterns

They are not a complete security solution. The red-team suite covers five direct attacks; it does not yet cover document injection, multi-turn attacks, or comprehensive adversarial testing.

## Current Scope

Implemented:

- Multi-turn RAG support assistant
- Conversation persistence across application restarts
- Qdrant document retrieval
- Groq LLM integration
- Docker packaging
- Automated offline tests and CI
- Limited guardrails and red-team evaluation

Not implemented:

- Cross-conversation long-term memory
- TRL fine-tuning
- vLLM serving
- Comprehensive multi-turn coherence testing
- Measured security-improvement metrics

## License

Add a license before publishing or sharing the repository publicly.
