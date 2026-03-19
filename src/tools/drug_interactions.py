from langchain_core.tools import tool

from src.services.drug_interaction import DrugInteractionService


@tool
def drug_interaction_checker(drug_a: str, drug_b: str) -> str:
    """Check for known interactions between two medications.

    Args:
        drug_a: Name of the first drug (e.g. 'warfarin').
        drug_b: Name of the second drug (e.g. 'aspirin').

    Returns:
        A description of any known interaction, severity level, and clinical recommendation.
    """
    result = DrugInteractionService.check(drug_a, drug_b)

    if result is None:
        return (
            f"No known interaction found between '{drug_a}' and '{drug_b}' "
            f"in the database. Note: absence of data does not guarantee safety. "
            f"Always consult a clinical pharmacist."
        )

    return result.format()
