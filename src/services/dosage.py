from src.db import get_session
from src.repositories.dosage import DosageRepository
from src.schemas.dosage import DosageInfo, DosageResult


class DosageService:
    @staticmethod
    def calculate(
        medication: str, weight_kg: float, age_years: int
    ) -> DosageResult:
        """Calculate dosage for a medication from the database.

        Raises:
            ValueError: If inputs are invalid or medication not found.
        """
        if weight_kg <= 0:
            raise ValueError("Weight must be a positive number.")
        if age_years < 0:
            raise ValueError("Age must be non-negative.")

        with get_session() as session:
            repo = DosageRepository(session)
            entity = repo.find_by_medication(medication)

            if entity is None:
                available = ", ".join(repo.list_all_names())
                raise ValueError(
                    f"'{medication}' not found. Available: {available}"
                )

            if age_years < entity.min_age:
                raise ValueError(
                    f"{medication} is not recommended under {entity.min_age} year(s). "
                    f"Consult a pediatric specialist."
                )

            info = DosageInfo(
                dose_mg_per_kg_min=entity.dose_mg_per_kg_min,
                dose_mg_per_kg_max=entity.dose_mg_per_kg_max,
                max_daily_mg=entity.max_daily_mg,
                frequency=entity.frequency,
                form=entity.form,
                min_age=entity.min_age,
                pediatric_note=entity.pediatric_note,
                adult_note=entity.adult_note,
                geriatric_note=entity.geriatric_note,
            )
            return info.calculate(weight_kg, age_years)
