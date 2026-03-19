from pydantic import BaseModel

from src.schemas.enums import BMICategory


class BMIResult(BaseModel):
    value: float
    category: BMICategory

    def format(self) -> str:
        risk_str = "\n".join(f"  - {r}" for r in self.category.risks)
        return (
            f"BMI: {self.value:.1f}\n"
            f"WHO Classification: {self.category.display_name}\n"
            f"Associated health risks:\n{risk_str}"
        )
