PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": ["gpt-5.4-mini", "gpt-5.4", "gpt-5.2"],
    "anthropic": ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"],
    "gigachat": ["GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max"],
    "ollama": ["llama3.1", "deepseek-r1", "qwen3", "phi4", "gemma2"],
}

TOOL_LABELS = {
    "drug_interaction_checker": "Drug Interactions",
    "bmi_calculator": "BMI Calculator",
    "icd10_search": "ICD-10 Search",
    "dosage_calculator": "Dosage Calculator",
    "medical_term_explainer": "Term Explainer",
    "search_medical_literature": "Web Search",
}

EXAMPLES = [
    "Можно ли принимать варфарин вместе с аспирином?",
    "Рассчитай ИМТ: вес 95 кг, рост 175 см",
    "Код МКБ-10 для сахарного диабета 2 типа",
    "Дозировка амоксициллина для ребёнка 30 кг, 8 лет",
    "Что такое тахикардия?",
    "Последние рекомендации по лечению гипертонии",
]
