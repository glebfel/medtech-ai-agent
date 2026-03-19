from pydantic import BaseModel


class DosageInfo(BaseModel):
    dose_mg_per_kg_min: float
    dose_mg_per_kg_max: float
    max_daily_mg: float
    frequency: str
    form: str
    pediatric_note: str
    adult_note: str
    geriatric_note: str
    min_age: float = 0

    def calculate(self, weight_kg: float, age_years: int) -> "DosageResult":
        dose_min = min(weight_kg * self.dose_mg_per_kg_min, self.max_daily_mg)
        dose_max = min(weight_kg * self.dose_mg_per_kg_max, self.max_daily_mg)

        if age_years < 18:
            note = self.pediatric_note
        elif age_years >= 65:
            note = self.geriatric_note
        else:
            note = self.adult_note

        return DosageResult(
            daily_dose_min_mg=dose_min,
            daily_dose_max_mg=dose_max,
            max_daily_mg=self.max_daily_mg,
            frequency=self.frequency,
            form=self.form,
            note=note,
        )


class DosageResult(BaseModel):
    daily_dose_min_mg: float
    daily_dose_max_mg: float
    max_daily_mg: float
    frequency: str
    form: str
    note: str

    def format(self, medication: str, weight_kg: float, age_years: int) -> str:
        return "\n".join(
            [
                f"Dosage calculation for {medication.upper()}:",
                f"  Patient: {weight_kg} kg, {age_years} years old",
                f"  Form: {self.form}",
                f"  Calculated daily dose: {self.daily_dose_min_mg:.0f} - {self.daily_dose_max_mg:.0f} mg/day",
                f"  Maximum daily dose: {self.max_daily_mg:.0f} mg/day",
                f"  Frequency: {self.frequency}",
                f"\n  Note: {self.note}",
                "\n  WARNING: This is a calculated estimate. Always verify with clinical "
                "guidelines and adjust for patient-specific factors.",
            ]
        )
