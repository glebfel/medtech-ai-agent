import json
import os
from collections.abc import Callable

from sqlalchemy.orm import Session

from src.logging_config import get_logger
from src.models.dosage import DosageInfoEntity
from src.models.drug_interaction import DrugInteractionEntity
from src.models.icd10 import ICD10CodeEntity
from src.models.med_term import MedTermEntity
from src.services.embeddings import embed_texts


logger = get_logger("db.seed")


def seed_if_empty(session: Session, data_dir: str = "data") -> None:
    _seed_table(
        session,
        data_dir=data_dir,
        filename="drug_interactions.json",
        entity_cls=DrugInteractionEntity,
        mapper=_map_drug_interaction,
    )
    _seed_table(
        session,
        data_dir=data_dir,
        filename="icd10_codes.json",
        entity_cls=ICD10CodeEntity,
        mapper=_map_icd10,
    )
    _seed_table(
        session,
        data_dir=data_dir,
        filename="med_terms.json",
        entity_cls=MedTermEntity,
        mapper=_map_med_term,
    )
    _seed_table(
        session,
        data_dir=data_dir,
        filename="dosages.json",
        entity_cls=DosageInfoEntity,
        mapper=_map_dosage,
    )

    _generate_embeddings_if_needed(session)


def _seed_table(
    session: Session, data_dir: str, filename: str, entity_cls: type, mapper: Callable
) -> None:
    if session.query(entity_cls).count() > 0:
        return

    path = os.path.join(data_dir, filename)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    entities = [mapper(item) for item in data]
    session.add_all(entities)
    session.flush()
    logger.info("Seeded %d %s records", len(entities), entity_cls.__tablename__)


def _generate_embeddings_if_needed(session: Session) -> None:
    # Med terms
    terms = session.query(MedTermEntity).filter(MedTermEntity.embedding.is_(None)).all()
    if terms:
        texts = [f"{t.term}: {t.explanation}" for t in terms]
        try:
            vectors = embed_texts(texts)
            for term, vec in zip(terms, vectors):
                term.embedding = vec
            session.flush()
            logger.info("Generated embeddings for %d med_terms", len(terms))
        except Exception as e:
            logger.error("Failed to generate med_terms embeddings: %s", e)

    # ICD-10
    codes = (
        session.query(ICD10CodeEntity).filter(ICD10CodeEntity.embedding.is_(None)).all()
    )
    if codes:
        texts = [f"{c.code}: {c.description}" for c in codes]
        try:
            vectors = embed_texts(texts)
            for code, vec in zip(codes, vectors):
                code.embedding = vec
            session.flush()
            logger.info("Generated embeddings for %d icd10_codes", len(codes))
        except Exception as e:
            logger.error("Failed to generate icd10 embeddings: %s", e)

    # Drug interactions
    interactions = (
        session.query(DrugInteractionEntity)
        .filter(DrugInteractionEntity.embedding.is_(None))
        .all()
    )
    if interactions:
        texts = [f"{i.drug_a} + {i.drug_b}: {i.description}" for i in interactions]
        try:
            vectors = embed_texts(texts)
            for interaction, vec in zip(interactions, vectors):
                interaction.embedding = vec
            session.flush()
            logger.info(
                "Generated embeddings for %d drug_interactions", len(interactions)
            )
        except Exception as e:
            logger.error("Failed to generate drug_interactions embeddings: %s", e)


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
