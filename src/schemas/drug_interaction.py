from pydantic import BaseModel

from src.schemas.enums import InteractionSeverity


class DrugInteractionDTO(BaseModel):
    drug_a: str
    drug_b: str
    severity: InteractionSeverity
    description: str
    recommendation: str

    def format(self) -> str:
        return (
            f"INTERACTION FOUND:\n"
            f"  Drugs: {self.drug_a} + {self.drug_b}\n"
            f"  Severity: {self.severity.label}\n"
            f"  Description: {self.description}\n"
            f"  Recommendation: {self.recommendation}"
        )
