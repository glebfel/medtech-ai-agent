# MedAssistAI — AI-агент клинической поддержки

LLM-агент для медицинских работников на базе LangGraph, LangChain, Streamlit и PostgreSQL.


## Возможности

- **6 инструментов:** проверка взаимодействий лекарств, расчёт ИМТ, поиск МКБ-10, расчёт дозировок, словарь мед. терминов, веб-поиск
- **Мульти-LLM:** OpenAI, Anthropic (Claude), GigaChat, Ollama (локальные модели)
- **Выбор модели в UI:** переключение провайдера и модели прямо в sidebar с индикацией статуса подключения
- **История чатов:** сохранение, поиск, переименование и удаление диалогов
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
├── services/            # Бизнес-логика (инфраструктура, сессии чатов)
├── tools/               # LangChain @tool обёртки (6 инструментов)
├── agent/               # LangGraph агент, фабрика LLM, промпты, health checks
└── ui/                  # Streamlit-компоненты (чат, sidebar, графики)
```

**Поток данных:** `Tool → Service → Repository → Entity → PostgreSQL`

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

Скрипт автоматически:
- проверит наличие Docker
- создаст `.env` из `.env.example` если нет
- соберёт и запустит контейнеры
- покажет URL приложения

### Ручной запуск (без Docker для приложения)

```bash
# 1. PostgreSQL
docker compose up -d postgres

# 2. Зависимости
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Конфигурация
cp .env.example .env
# отредактировать .env

# 4. Запуск
streamlit run src/main.py
```

## Подключение LLM-провайдеров

### OpenAI / Anthropic / GigaChat

Указать ключи в `.env`:

| Переменная | Когда нужна |
|---|---|
| `OPENAI_API_KEY` | `DEFAULT_LLM_PROVIDER=openai` |
| `ANTHROPIC_API_KEY` | `DEFAULT_LLM_PROVIDER=anthropic` |
| `GIGACHAT_CLIENT_ID` + `GIGACHAT_CLIENT_SECRET` | `DEFAULT_LLM_PROVIDER=gigachat` |

### Ollama (локальные модели)

Ollama поднимается автоматически как Docker-сервис вместе с приложением. API-ключи не нужны.

Скачивание и выбор моделей — прямо из UI: выбрать провайдер Ollama в sidebar, раскрыть "Pull new model", ввести имя модели и нажать Pull.

Популярные модели: `llama3.1`, `deepseek-r1`, `qwen3`, `phi4`, `gemma2`.

## Справочник конфигурации

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DEFAULT_LLM_PROVIDER` | `openai` | LLM-бэкенд: `openai`, `anthropic`, `gigachat`, `ollama` |
| `OPENAI_API_KEY` | | Ключ OpenAI API |
| `ANTHROPIC_API_KEY` | | Ключ Anthropic API |
| `GIGACHAT_CLIENT_ID` | | Client ID GigaChat |
| `GIGACHAT_CLIENT_SECRET` | | Client Secret GigaChat |
| `GIGACHAT_SCOPE` | `GIGACHAT_API_PERS` | Scope GigaChat API |
| `GIGACHAT_VERIFY_SSL` | `false` | Проверка SSL для GigaChat |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | URL сервера Ollama |
| `HEALTH_CHECK_TIMEOUT` | `5` | Таймаут проверки подключения провайдеров (сек) |
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
- **LLM:** OpenAI / Anthropic (Claude) / GigaChat / Ollama
- **UI:** Streamlit + Plotly
- **БД:** PostgreSQL 16 + SQLAlchemy 2.0 + Alembic
- **Поиск:** pg_trgm (триграммное сходство), DuckDuckGo
- **Наблюдаемость:** Python logging, LangSmith (опционально)
