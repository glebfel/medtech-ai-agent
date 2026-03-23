# MedAssistAI — AI-агент клинической поддержки

LLM-агент для медицинских работников на базе LangGraph, LangChain, Streamlit и PostgreSQL.

## Возможности

- **8 инструментов:** проверка взаимодействий лекарств, расчёт ИМТ, поиск МКБ-10, расчёт дозировок, словарь мед. терминов, веб-поиск, сохранение/поиск фактов о пациенте
- **Мульти-LLM:** OpenAI, Anthropic (Claude), GigaChat, Ollama (локальные модели)
- **Выбор модели в UI:** переключение провайдера и модели в sidebar с индикацией статуса подключения
- **Семантический поиск:** pgvector + nomic-embed-text для поиска по смыслу в мед. терминах и МКБ-10
- **Память пользователя:** LangMem + LangGraph Store + pgvector — агент запоминает факты о пациенте и ищет по смыслу
- **История чатов:** сохранение, поиск, переименование и удаление диалогов
- **Персистентная память:** состояние диалога хранится в PostgreSQL через LangGraph checkpointer
- **Веб-интерфейс:** Streamlit с gauge-диаграммой ИМТ, таблицей МКБ-10, управлением памятью
- **Наблюдаемость:** структурированное логирование, опциональный трейсинг через LangSmith

## Архитектура

> Подробная документация с диаграммами: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

```
src/
├── settings.py          # Конфигурация (pydantic-settings)
├── main.py              # Точка входа (Streamlit)
├── schemas/             # Pydantic DTO + enums
├── models/              # SQLAlchemy ORM-сущности + pgvector
├── db/                  # Engine, сессии, сидирование + embeddings
├── repositories/        # Слой доступа к данным (SQL + vector search)
├── services/            # Бизнес-логика, embeddings, chat sessions
├── tools/               # LangChain @tool обёртки (6 мед. инструментов)
├── agent/               # LangGraph агент, LLM factory, LangMem memory, промпты
└── ui/                  # Streamlit-компоненты (чат, sidebar, графики)
```

## Быстрый старт

### Docker (рекомендуется)

```bash
cp .env.example .env
# заполнить ключи LLM в .env
docker compose up --build
```

Открыть http://localhost:8501

### Скрипт быстрого запуска

```bash
./scripts/start.sh
```

### Ручной запуск

```bash
docker compose up -d postgres ollama
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run src/main.py
```

## Подключение LLM-провайдеров

Указать ключи в `.env`. Провайдер переключается через UI в любой момент.

| Провайдер | Переменные |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| GigaChat | `GIGACHAT_CLIENT_ID` + `GIGACHAT_CLIENT_SECRET` |
| Ollama | `OLLAMA_BASE_URL` (без API-ключей) |

Ollama: скачивание моделей прямо из UI (sidebar → Pull new model).

## Конфигурация

Полный справочник переменных окружения: [docs/ARCHITECTURE.md#справочник-конфигурации](docs/ARCHITECTURE.md#справочник-конфигурации)

## Демо-сценарии

| Запрос | Инструмент |
|---|---|
| Можно ли принимать варфарин с аспирином? | drug_interaction_checker |
| Рассчитай ИМТ: вес 95 кг, рост 175 см | bmi_calculator + gauge-диаграмма |
| Код МКБ-10 для диабета 2 типа | icd10_search (pgvector) |
| Дозировка амоксициллина для ребёнка 30 кг, 8 лет | dosage_calculator |
| Что такое тахикардия? / учащённое сердцебиение | medical_term_explainer (pgvector) |
| Последние рекомендации по лечению гипертонии | search_medical_literature |
| Мне 45 лет, принимаю варфарин | save_memory (LangMem) |
| Какие у меня аллергии? | search_memory (LangMem) |

## Стек технологий

- **Агент:** LangGraph (ReAct), LangChain, LangMem
- **LLM:** OpenAI / Anthropic / GigaChat / Ollama
- **Память:** LangGraph Store + LangMem (user memory), PostgreSQL Checkpointer
- **Поиск:** pgvector + nomic-embed-text (семантический), DuckDuckGo (веб)
- **UI:** Streamlit + Plotly
- **БД:** PostgreSQL 16 + pgvector + SQLAlchemy 2.0 + Alembic
- **Наблюдаемость:** LangSmith, Python logging
- **Инфраструктура:** Docker Compose, Ollama, Ruff + pre-commit
