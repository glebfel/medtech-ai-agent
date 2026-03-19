from src.schemas.bmi import BMIResult
from src.schemas.enums import BMICategory


class BMIService:
    @staticmethod
    def calculate(weight_kg: float, height_cm: float) -> BMIResult:
        """Calculate BMI and classify per WHO categories.

        Raises:
            ValueError: If weight or height are not positive.
        """
        if weight_kg <= 0 or height_cm <= 0:
            raise ValueError("Weight and height must be positive numbers.")

        bmi_value = weight_kg / (height_cm / 100.0) ** 2
        category = BMICategory.from_bmi(bmi_value)

        return BMIResult(value=bmi_value, category=category)
