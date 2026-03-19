from src.tools.bmi_calculator import bmi_calculator
from src.tools.dosage_calculator import dosage_calculator
from src.tools.drug_interactions import drug_interaction_checker
from src.tools.icd10_search import icd10_search
from src.tools.med_terms import medical_term_explainer
from src.tools.web_search import search_medical_literature

all_tools = [
    drug_interaction_checker,
    bmi_calculator,
    icd10_search,
    dosage_calculator,
    medical_term_explainer,
    search_medical_literature,
]
