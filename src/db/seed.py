import json
import os

from sqlalchemy.orm import Session

from src.logging_config import get_logger
from src.models.dosage import DosageInfoEntity
from src.models.drug_interaction import DrugInteractionEntity
from src.models.icd10 import ICD10CodeEntity
from src.models.med_term import MedTermEntity


logger = get_logger("db.seed")


def seed_if_empty(session: Session, data_dir: str = "data") -> None:
    """Seed all reference tables from JSON files if they are empty."""
    _seed_table(session, data_dir=data_dir, filename="drug_interactions.json", entity_cls=DrugInteractionEntity, mapper=_map_drug_interaction)
    _seed_table(session, data_dir=data_dir, filename="icd10_codes.json", entity_cls=ICD10CodeEntity, mapper=_map_icd10)
    _seed_table(session, data_dir=data_dir, filename="med_terms.json", entity_cls=MedTermEntity, mapper=_map_med_term)
    _seed_table(session, data_dir=data_dir, filename="dosages.json", entity_cls=DosageInfoEntity, mapper=_map_dosage)


def _seed_table(session, data_dir, filename, entity_cls, mapper) -> None:
    if session.query(entity_cls).count() > 0:
        return

    path = os.path.join(data_dir, filename)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    entities = [mapper(item) for item in data]
    session.add_all(entities)
    session.flush()
    logger.info("Seeded %d %s records", len(entities), entity_cls.__tablename__)


def _map_drug_interaction(item: dict) -> DrugInteractionEntity:
    return DrugInteractionEntity(
        drug_a=item["drug_a"],
        drug_b=item["drug_b"],
        severity=item["severity"],
        description=item["description"],
        recommendation=item["recommendation"],
    )


def _map_icd10(item: dict) -> ICD10CodeEntity:
    return ICD10CodeEntity(code=item["code"], description=item["description"])


def _map_med_term(item: dict) -> MedTermEntity:
    return MedTermEntity(term=item["term"], explanation=item["explanation"])


def _map_dosage(item: dict) -> DosageInfoEntity:
    return DosageInfoEntity(
        medication=item["medication"],
        dose_mg_per_kg_min=item["dose_mg_per_kg_min"],
        dose_mg_per_kg_max=item["dose_mg_per_kg_max"],
        max_daily_mg=item["max_daily_mg"],
        frequency=item["frequency"],
        form=item["form"],
        min_age=item.get("min_age", 0),
        pediatric_note=item["pediatric_note"],
        adult_note=item["adult_note"],
        geriatric_note=item["geriatric_note"],
    )
