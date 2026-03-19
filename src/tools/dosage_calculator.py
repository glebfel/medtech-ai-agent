from langchain_core.tools import tool

from src.services.dosage import DosageService


@tool
def dosage_calculator(medication: str, weight_kg: float, age_years: int) -> str:
    """Calculate recommended medication dosage based on patient weight and age.

    Args:
        medication: Name of the medication (e.g. 'amoxicillin', 'ibuprofen', 'paracetamol').
        weight_kg: Patient weight in kilograms.
        age_years: Patient age in years.

    Returns:
        Recommended dosage range, frequency, and age-specific warnings.
    """
    try:
        result = DosageService.calculate(medication, weight_kg, age_years)
        return result.format(medication, weight_kg, age_years)
    except ValueError as e:
        return f"Error: {e}"
