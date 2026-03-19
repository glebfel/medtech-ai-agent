from typing import Optional

from src.db import get_session
from src.schemas.drug_interaction import DrugInteractionDTO
from src.schemas.enums import InteractionSeverity
from src.repositories.drug_interaction import DrugInteractionRepository


class DrugInteractionService:
    @staticmethod
    def check(drug_a: str, drug_b: str) -> Optional[DrugInteractionDTO]:
        """Check for known interaction between two drugs.

        Returns DrugInteractionDTO if found, None otherwise.
        """
        with get_session() as session:
            repo = DrugInteractionRepository(session)
            entity = repo.find_by_drug_pair(drug_a, drug_b)

            if entity is None:
                return None

            return DrugInteractionDTO(
                drug_a=entity.drug_a,
                drug_b=entity.drug_b,
                severity=InteractionSeverity(entity.severity),
                description=entity.description,
                recommendation=entity.recommendation,
            )
