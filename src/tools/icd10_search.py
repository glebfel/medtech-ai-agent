from langchain_core.tools import tool

from src.services.icd10 import ICD10Service


@tool
def icd10_search(query: str) -> str:
    """Search ICD-10 diagnosis codes by description keywords.

    Args:
        query: Search terms describing a diagnosis (e.g. 'acute bronchitis', 'type 2 diabetes').

    Returns:
        Up to 5 matching ICD-10 codes with descriptions and match confidence.
    """
    results = ICD10Service.search(query, limit=5)

    if not results:
        return f"No ICD-10 codes found matching '{query}'. Try different keywords."

    lines = [f"ICD-10 search results for '{query}':\n"]
    lines.extend(r.format() for r in results)
    lines.append(
        "\nNote: Always verify codes against the official ICD-10-CM reference."
    )

    return "\n".join(lines)
