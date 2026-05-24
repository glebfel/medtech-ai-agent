# MedAssistAI — Clinical Support AI Agent

LLM agent for medical professionals built on LangGraph, LangChain, Streamlit, and PostgreSQL.

## Features

- **8 tools:** drug interaction checker, BMI calculator, ICD-10 search, dosage calculator, medical term dictionary, web search, save/search patient facts
- **Multi-LLM:** OpenAI, Anthropic (Claude), GigaChat, Ollama (local models)
- **Model selection in UI:** switch provider and model in the sidebar with a connection status indicator
- **Semantic search:** pgvector + nomic-embed-text for meaning-based search across medical terms and ICD-10
- **User memory:** LangMem + LangGraph Store + pgvector — the agent remembers patient facts and searches by meaning
- **Chat history:** save, search, rename, and delete conversations
- **Persistent memory:** conversation state stored in PostgreSQL via the LangGraph checkpointer
- **Web interface:** Streamlit with a BMI gauge chart, ICD-10 table, and memory management
- **Observability:** structured logging, optional tracing via LangSmith

## Architecture

> Detailed documentation with diagrams: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

```
src/
├── settings.py          # Configuration (pydantic-settings)
├── main.py              # Entry point (Streamlit)
├── schemas/             # Pydantic DTOs + enums
├── models/              # SQLAlchemy ORM entities + pgvector
├── db/                  # Engine, sessions, seeding + embeddings
├── repositories/        # Data access layer (SQL + vector search)
├── services/            # Business logic, embeddings, chat sessions
├── tools/               # LangChain @tool wrappers (6 medical tools)
├── agent/               # LangGraph agent, LLM factory, LangMem memory, prompts
└── ui/                  # Streamlit components (chat, sidebar, charts)
```

## Quick start

### Docker (recommended)

```bash
cp .env.example .env
# fill in LLM keys in .env
docker compose up --build
```

Open http://localhost:8501

### Quick start script

```bash
./scripts/start.sh
```

### Manual start

```bash
docker compose up -d postgres ollama
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run src/main.py
```

## LLM provider setup

Set the keys in `.env`. You can switch the provider in the UI at any time.

| Provider | Variables |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| GigaChat | `GIGACHAT_CLIENT_ID` + `GIGACHAT_CLIENT_SECRET` |
| Ollama | `OLLAMA_BASE_URL` (no API keys required) |

Ollama: download models directly from the UI (sidebar → Pull new model).

## Configuration

Full environment variables reference: [docs/ARCHITECTURE.md#configuration-reference](docs/ARCHITECTURE.md#configuration-reference)

## Demo scenarios

| Request | Tool |
|---|---|
| Can warfarin be taken with aspirin? | drug_interaction_checker |
| Calculate BMI: weight 95 kg, height 175 cm | bmi_calculator + gauge chart |
| ICD-10 code for type 2 diabetes | icd10_search (pgvector) |
| Amoxicillin dosage for a child weighing 30 kg, age 8 | dosage_calculator |
| What is tachycardia? / rapid heartbeat | medical_term_explainer (pgvector) |
| Latest recommendations for treating hypertension | search_medical_literature |
| I'm 45 years old, taking warfarin | save_memory (LangMem) |
| What allergies do I have? | search_memory (LangMem) |

## Technology stack

- **Agent:** LangGraph (ReAct), LangChain, LangMem
- **LLM:** OpenAI / Anthropic / GigaChat / Ollama
- **Memory:** LangGraph Store + LangMem (user memory), PostgreSQL Checkpointer
- **Search:** pgvector + nomic-embed-text (semantic), DuckDuckGo (web)
- **UI:** Streamlit + Plotly
- **Database:** PostgreSQL 16 + pgvector + SQLAlchemy 2.0 + Alembic
- **Observability:** LangSmith, Python logging
- **Infrastructure:** Docker Compose, Ollama, Ruff + pre-commit
