# MedAssist — AI-агент клинической поддержки

LLM-агент для медицинских работников на базе LangGraph, LangChain, Streamlit и PostgreSQL.


## Возможности

- **6 инструментов:** проверка взаимодействий лекарств, расчёт ИМТ, поиск МКБ-10, расчёт дозировок, словарь мед. терминов, веб-поиск
- **Мульти-LLM:** OpenAI, GigaChat, Ollama (локальные модели)
- **Персистентная память:** состояние диалога хранится в PostgreSQL через LangGraph checkpointer
- **Веб-интерфейс:** Streamlit с sidebar настройками, gauge-диаграмма ИМТ, таблица результатов МКБ-10, статистика вызовов
- **Справочные данные в PostgreSQL:** взаимодействия лекарств, коды МКБ-10, мед. термины, дозировки — сидируются из JSON при первом запуске
- **Миграции БД:** Alembic для версионирования схемы
- **Наблюдаемость:** структурированное логирование, опциональный трейсинг через LangSmith

## Архитектура

```
src/
├── settings.py          # Конфигурация (pydantic-settings)
├── logging_config.py    # Настройка логирования
├── main.py              # Точка входа (Streamlit)
├── schemas/             # Pydantic DTO + enums
├── models/              # SQLAlchemy ORM-сущности
├── db/                  # Engine, сессии, сидирование
├── repositories/        # Слой доступа к данным (SQL-запросы)
├── services/            # Бизнес-логика
├── tools/               # LangChain @tool обёртки (6 инструментов)
├── agent/               # LangGraph агент, фабрика LLM, промпты
└── ui/                  # Streamlit-компоненты (чат, sidebar, графики)
```

**Поток данных:** `Tool → Service → Repository → Entity → PostgreSQL`

## Быстрый старт

### 1. Предварительные требования

- Python 3.11+
- Docker (для PostgreSQL)

### 2. Запуск PostgreSQL

```bash
docker compose up -d postgres
```

### 3. Установка зависимостей

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 4. Конфигурация

```bash
cp .env.example .env
```

Отредактировать `.env` — указать ключи LLM-провайдера:

| Переменная | Когда нужна |
|---|---|
| `OPENAI_API_KEY` | `LLM_PROVIDER=openai` |
| `GIGACHAT_CREDENTIALS` | `LLM_PROVIDER=gigachat` |
| Запущенный Ollama | `LLM_PROVIDER=ollama` |

### 5. Запуск

```bash
streamlit run src/main.py
```

Открыть http://localhost:8501

### Docker (полный стек)

```bash
cp .env.example .env
# заполнить ключи LLM
docker compose up --build
```

Открыть http://localhost:8501

## Справочник конфигурации

| Переменная | По умолчанию | Описание |
|---|---|---|
| `LLM_PROVIDER` | `openai` | LLM-бэкенд: `openai`, `gigachat`, `ollama` |
| `OPENAI_API_KEY` | | Ключ OpenAI API |
| `OPENAI_MODEL` | `gpt-4o-mini` | Модель OpenAI |
| `GIGACHAT_CREDENTIALS` | | Креды GigaChat |
| `GIGACHAT_VERIFY_SSL` | `false` | Проверка SSL для GigaChat |
| `OLLAMA_MODEL` | `llama3.1` | Модель Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL сервера Ollama |
| `DB_HOST` | `localhost` | Хост PostgreSQL |
| `DB_PORT` | `5432` | Порт PostgreSQL |
| `DB_NAME` | `medassist` | Имя базы данных |
| `DB_USER` | `medassist` | Пользователь БД |
| `DB_PASSWORD` | `medassist` | Пароль БД |
| `DB_POOL_SIZE` | `5` | Размер пула соединений |
| `DB_MAX_OVERFLOW` | `10` | Макс. доп. соединений сверх пула |
| `LOG_LEVEL` | `INFO` | Уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LANGCHAIN_TRACING_V2` | `false` | Включить трейсинг LangSmith |
| `LANGCHAIN_API_KEY` | | Ключ LangSmith API |
| `LANGCHAIN_PROJECT` | `medassist` | Имя проекта в LangSmith |

## Миграции БД

Миграции управляются через Alembic и запускаются автоматически при старте приложения.

Создание новой миграции после изменения ORM-моделей:

```bash
alembic revision --autogenerate -m "описание изменений"
```

Ручное применение:

```bash
alembic upgrade head
```

## Демо-сценарии

| Запрос | Вызываемый инструмент |
|---|---|
| Можно ли принимать варфарин с аспирином? | drug_interaction_checker |
| Рассчитай ИМТ: вес 95 кг, рост 175 см | bmi_calculator + gauge-диаграмма |
| Код МКБ-10 для диабета 2 типа | icd10_search + таблица результатов |
| Дозировка амоксициллина для ребёнка 30 кг, 8 лет | dosage_calculator |
| Что такое тахикардия? | medical_term_explainer |
| Последние рекомендации по лечению гипертонии | search_medical_literature |

## Стек технологий

- **Агент:** LangGraph (ReAct-паттерн), LangChain
- **LLM:** OpenAI / GigaChat / Ollama
- **UI:** Streamlit + Plotly
- **БД:** PostgreSQL 16 + SQLAlchemy 2.0 + Alembic
- **Поиск:** pg_trgm (триграммное сходство), DuckDuckGo
- **Наблюдаемость:** Python logging, LangSmith (опционально)
