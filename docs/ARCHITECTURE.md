# MedAssistAI — Architecture Documentation

## Overview

MedAssistAI is an AI-powered clinical decision support system built on a ReAct agent architecture (Reasoning + Acting). The system uses LangGraph to orchestrate the agent, LangChain for LLM/tool abstractions, Streamlit for the web interface, and PostgreSQL for data storage.

![System overview](images/overview.png)

---

## Request lifecycle

Full path of a user message from input to displayed response:

![Request lifecycle](images/request_lifecycle.png)

---

## Layered architecture

The application follows a clean layered architecture:

![Layered architecture](images/layer_architecture.png)

**Data flow:** `Tool → Service → Repository → Entity → PostgreSQL`

---

## Memory architecture

The system uses three kinds of memory:

- **Short-term** — `st.session_state.messages`, lives as long as the browser tab is open
- **Long-term** — LangGraph Checkpointer (conversation state), LangGraph Store (patient facts), chat_sessions table (metadata)
- **Semantic** — pgvector embeddings for meaning-based search across medical terms, ICD-10, and drug interactions

![Memory architecture](images/memory_architecture.png)

Highlights:
- **LangMem** — `save_memory` / `search_memory` tools for storing and retrieving patient facts (semantic search via pgvector + nomic-embed-text)
- **Memory Extractor** — a fallback mechanism for providers that do not call `save_memory` via tool calling (e.g., GigaChat). After the agent responds, a separate LLM call is made to extract personal medical facts from the user message. If the agent has already called `save_memory`, the extractor is skipped
- **90-day TTL** — stale facts are removed automatically (sweep every 60 min)
- **Patient Memory UI** — the user can see and delete saved facts in the sidebar
- **User ID** — memory is isolated per user via a browser cookie (365 days)

---

## Tool pipeline

The agent has access to 8 tools:

| # | Tool | Parameters | Description |
|---|-----------|-----------|----------|
| 1 | `drug_interaction_checker` | drug_a, drug_b | Check drug interactions |
| 2 | `bmi_calculator` | weight_kg, height_cm | Calculate BMI + WHO classification |
| 3 | `icd10_search` | query | Semantic search of ICD-10 codes |
| 4 | `dosage_calculator` | medication, weight_kg, age_years | Calculate dosage by weight/age |
| 5 | `medical_term_explainer` | term | Semantic search of medical terms |
| 6 | `search_medical_literature` | query | Web search (DuckDuckGo) |
| 7 | `save_memory` | content | Save patient facts (LangMem) |
| 8 | `search_memory` | query | Search saved facts (LangMem) |

![Tool pipeline](images/tool_pipeline.png)

Each medical tool follows the chain: `@tool → Service → Repository → PostgreSQL/pgvector`

---

## LLM provider architecture

Four providers are supported and switchable from the UI:

| Provider | Models | Connection |
|-----------|--------|------------|
| **OpenAI** | gpt-5.4-mini, gpt-5.4, gpt-5.2 | API key |
| **Anthropic** | claude-haiku-4-5, claude-sonnet-4-6, claude-opus-4-6 | API key |
| **GigaChat** | GigaChat-2, GigaChat-2-Pro, GigaChat-2-Max | Client ID + Secret |
| **Ollama** | llama3.1, qwen3, phi4, gemma2 | Local (Docker) |

![LLM provider architecture](images/llm_providers.png)

Highlights:
- Model lists are fetched dynamically from each provider's API
- Health check per provider (5-min cache) with a UI indicator (✅ / ⬜ / ❌)
- Ollama: download models from the UI, incompatible models (no tool calling) are filtered out
- Embedding model (`nomic-embed-text`) is separate, fixed, and served via Ollama

---

## Database schema

![Database schema](images/database_schema.png)

**Main tables:**
- `drug_interactions` — drug interaction reference (43 entries)
- `icd10_codes` — ICD-10 codes (157 entries)
- `med_terms` — medical terms (54 entries)
- `dosage_info` — drug dosages (11 entries)
- `chat_sessions` — chat metadata (title, thread_id, dates)

**pgvector:** `embedding vector(768)` columns in drug_interactions, icd10_codes, med_terms for semantic search

**LangGraph:** checkpoints (agent state) and store (patient facts) tables

---

## ReAct agent pattern

![ReAct pattern](images/react_pattern.png)

Agent loop:
1. **pre_model_hook** — trim_messages by token budget (32K tokens, protects against context overflow)
2. **LLM Reasoning** — the model decides whether a tool call is needed
3. **Tool Execution** — if yes, the tool is invoked
4. **LLM Response** — the model produces the final answer based on the result
5. **Checkpointer** — state is persisted to PostgreSQL

---

## Docker Compose

![Docker Compose](images/docker_compose.png)

Four services:
- **postgres** (pgvector/pgvector:pg16) — database, port 5433
- **ollama** (ollama/ollama) — local models, port 11434
- **ollama-init** — init container, downloads the embedding model on first run
- **app** (Streamlit) — application, port 8501

Startup order: postgres (healthcheck) + ollama (healthcheck) → ollama-init (pull model) → app

---

## Security

![Security](images/security.png)

| Measure | Description |
|------|----------|
| **Prompt Injection** | Prompt disclosure is forbidden; "ignore previous instructions" is rejected |
| **Input validation** | max_input_length (5000), empty messages rejected |
| **Error sanitization** | API keys are stripped from error messages |
| **Query filtering** | Non-medical questions are rejected without invoking tools |
| **Context protection** | trim_messages by token budget (32K), truncation at HumanMessage boundary |
| **Secrets** | Pydantic SecretStr, .env file, Base64 for GigaChat |

---

## Observability

![Observability](images/observability.png)

| Component | Coverage |
|-----------|--------------|
| **LangSmith** (optional) | Tracing of LLM calls, latency, tokens, cost, tool calls |
| **Python Logging** | Infrastructure (DB, migrations), health checks, request timing, errors |
| **UI indicators** | Connection status for each provider in the sidebar |

---

## Configuration reference

All settings are configured via environment variables (`.env` file):

| Category | Variable | Default | Description |
|-----------|-----------|-------------|----------|
| **TLS** | `VERIFY_SSL` | `true` | Verify TLS certificates for all external services (disable behind a corporate proxy) |
| **LLM** | `DEFAULT_LLM_PROVIDER` | `openai` | Default provider |
| **OpenAI** | `OPENAI_API_KEY` | — | API key |
| **Anthropic** | `ANTHROPIC_API_KEY` | — | API key |
| **GigaChat** | `GIGACHAT_CLIENT_ID` | — | OAuth Client ID |
| | `GIGACHAT_CLIENT_SECRET` | — | OAuth Client Secret |
| **Ollama** | `OLLAMA_BASE_URL` | `http://ollama:11434` | Server URL |
| **Embeddings** | `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |
| | `EMBEDDING_DIM` | `768` | Vector dimensionality |
| **Health** | `HEALTH_CHECK_TIMEOUT` | `5` | Provider check timeout (sec) |
| **User** | `USER_STORAGE_KEY` | `medassist_user_id` | Browser cookie key |
| | `USER_COOKIE_MAX_AGE_DAYS` | `365` | Cookie lifetime (days) |
| **Memory** | `MEMORY_TTL_DAYS` | `90` | Fact retention (0 = unlimited) |
| | `MEMORY_SWEEP_INTERVAL_MINUTES` | `60` | Cleanup interval for stale facts |
| **Limits** | `MAX_INPUT_LENGTH` | `5000` | Max message length (characters) |
| | `MAX_CONTEXT_TOKENS` | `32000` | LLM context token budget |
| | `MAX_VISIBLE_CHATS` | `15` | Number of chats in the sidebar |
| **Database** | `DB_HOST` | `localhost` | PostgreSQL host |
| | `DB_PORT` | `5432` | PostgreSQL port |
| | `DB_POOL_SIZE` | `5` | Connection pool size |
| **Logging** | `LOG_LEVEL` | `INFO` | Logging level |
| **Tracing** | `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith |

---

## Technology stack

| Component | Technology | Purpose |
|-----------|-----------|-----------|
| Agent framework | LangGraph (ReAct) | Agent orchestration, state machine |
| LLM abstraction | LangChain | Provider-agnostic LLM/tools interface |
| User memory | LangMem + LangGraph Store | Save/search patient facts across sessions |
| Semantic search | pgvector + nomic-embed-text | Vector search over medical terms, ICD-10 |
| Web interface | Streamlit | Interactive medical assistant |
| Database | PostgreSQL 16 + pgvector | Reference data, sessions, checkpoints, embeddings |
| ORM | SQLAlchemy 2.0 | Data access layer |
| Migrations | Alembic | DB schema versioning |
| Visualization | Plotly | BMI gauge chart |
| Web search | DuckDuckGo (ddgs) | Medical literature search |
| Observability | LangSmith | LLM tracing, latency, tokens |
| Containerization | Docker Compose | Multi-service deployment |
| Local LLMs | Ollama | Local inference + embeddings |
| Code quality | Ruff + pre-commit | Linting and formatting |
