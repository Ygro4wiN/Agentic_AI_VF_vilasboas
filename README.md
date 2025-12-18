# Audit Assistant (Agentic AI)

Local setup for the **Audit Assistant** using **Docker Compose**, **Ollama**, and **RAG (Retrieval-Augmented Generation)**.

This README is designed so that **any group member can run the project locally without prior context**.

---

## Architecture (important)

This project runs **fully inside Docker**.

- The API runs in a container called **`audit-api`**
- Ollama runs in a container called **`ollama`**
- Containers communicate via the **Docker internal network**
- **Never use `localhost` inside containers**
- The Ollama endpoint used by the API is:

```text
http://ollama:11434
```

Models are downloaded **inside the Ollama container** and persisted using a Docker volume.

---

## Prerequisites

- Git
- Docker Desktop (running)

---

## Project layout

```text
audit-assistant/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .env                  # local only (do not commit)
├── data/
│   ├── docs/              # PDF documents used by RAG (REQUIRED)
│   └── sample.csv         # optional CSV example
├── src/
│   ├── server/
│   ├── rag/
│   ├── memory/
│   ├── tools/
│   └── observability/
└── README.md
```

⚠️ **Important**: The folder `data/docs` **must exist** and contain **at least one PDF**.  
If it is missing or empty, the `/ask` endpoint will return an error.

---

## Environment variables

Copy the example file:

```bash
cp .env.example .env
```

Required variables:

```env
# Ollama endpoint (Docker internal network)
OLLAMA_BASE_URL=http://ollama:11434

# Main LLM model
OLLAMA_MODEL=qwen2.5:7b
```

⚠️ Notes:
- Do **not** use `localhost`
- The API runs inside Docker, not on your host machine

---

## Run locally (first time)

```bash
git clone https://github.com/catarinatorres26/Agentic_AI_VF.git
cd Agentic_AI_VF/audit-assistant

# Environment
cp .env.example .env

# Start Ollama
docker compose up -d ollama

# Download required models (inside the Ollama container)
docker exec -it ollama ollama pull qwen2.5:7b
docker exec -it ollama ollama pull nomic-embed-text

# Start the API
docker compose up --build api
```

### Verify containers

```bash
docker ps
```

You should see:
- `ollama` → Up
- `audit-api` → Up

---

## Health check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "audit-assistant",
  "model": "qwen2.5:7b"
}
```

---

## Ask the agent

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"O que é uma auditoria de desempenho segundo as ISSAI?"}'
```

The answer is generated using:
- PDFs in `data/docs`
- RAG (vector search with embeddings)
- Qwen2.5 (7B) via Ollama

---

## Analyze a CSV

```bash
curl -X POST http://localhost:8000/analyze_csv \
  -F "file=@data/sample.csv"
```

---

## Preferences (memory)

Get preferences:

```bash
curl http://localhost:8000/preferences
```

Update preferences:

```bash
curl -X POST http://localhost:8000/preferences \
  -H "Content-Type: application/json" \
  -d '{"answer_style":"bullets","language":"pt","require_sources":true}'
```

---

## Common problems & fixes

### 1. `/ask` returns HTTP 500

Check if models exist:

```bash
docker exec -it ollama ollama list
```

Required:
- `qwen2.5:7b`
- `nomic-embed-text`

---

### 2. "Failed to connect to Ollama"

Cause:
- API trying to connect to `localhost`

Fix:

```env
OLLAMA_BASE_URL=http://ollama:11434
```

---

### 3. Error about missing PDFs

Cause:
- Folder `data/docs` missing or empty

Fix:
- Add at least one PDF to:

```text
audit-assistant/data/docs
```

---

## Notes

- Models are downloaded **only once** and reused via Docker volumes
- The setup is fully reproducible across machines
- This project is intended for **academic and experimental use**

---

## License

Academic / educational use only.

