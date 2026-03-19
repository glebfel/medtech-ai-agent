from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

_ddg = DuckDuckGoSearchRun()


@tool
def search_medical_literature(query: str) -> str:
    """Search the web for recent medical research, clinical guidelines, or health information.

    Args:
        query: The medical topic to search for (e.g. 'latest hypertension treatment guidelines 2025').

    Returns:
        Summary of relevant search results from the web.
    """
    search_query = f"medical research {query}"
    try:
        result = _ddg.invoke(search_query)
        return f"Web search results for '{query}':\n\n{result}"
    except Exception as e:
        return (
            f"Web search temporarily unavailable: {e}\n"
            f"Please try again later or consult PubMed, UpToDate, or Cochrane Library directly."
        )
