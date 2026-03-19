from langchain_core.tools import tool

from src.services.med_terms import MedTermsService


@tool
def medical_term_explainer(term: str) -> str:
    """Explain a medical term or abbreviation in simple, plain language.

    Args:
        term: The medical term or abbreviation to explain (e.g. 'tachycardia', 'CBC', 'dyspnea').

    Returns:
        A plain-language explanation of the medical term.
    """
    result = MedTermsService.explain(term)

    if result is None:
        return (
            f"'{term}' not found in the terminology database. "
            f"Try a different term or use the web search tool."
        )

    return result
