from langchain_core.tools import tool

from src.services.bmi import BMIService


@tool
def bmi_calculator(weight_kg: float, height_cm: float) -> str:
    """Calculate Body Mass Index and provide health risk assessment.

    Args:
        weight_kg: Patient weight in kilograms.
        height_cm: Patient height in centimeters.

    Returns:
        BMI value, WHO classification, and associated health risks.
    """
    try:
        result = BMIService.calculate(weight_kg, height_cm)
        return result.format()
    except ValueError as e:
        return f"Error: {e}"
