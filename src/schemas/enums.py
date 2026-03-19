from enum import StrEnum


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(StrEnum):
    OPENAI = "openai"
    GIGACHAT = "gigachat"
    OLLAMA = "ollama"


class InteractionSeverity(StrEnum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"

    @property
    def label(self) -> str:
        labels = {
            self.MINOR: "MINOR — low clinical significance",
            self.MODERATE: "MODERATE — may require dose adjustment or monitoring",
            self.MAJOR: "MAJOR — avoid combination or use with extreme caution",
            self.CONTRAINDICATED: "CONTRAINDICATED — must not be used together",
        }
        return labels[self]


class BMICategory(StrEnum):
    SEVERE_UNDERWEIGHT = "severe_underweight"
    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESITY_I = "obesity_class_i"
    OBESITY_II = "obesity_class_ii"
    OBESITY_III = "obesity_class_iii"

    @property
    def display_name(self) -> str:
        names = {
            self.SEVERE_UNDERWEIGHT: "Severe underweight",
            self.UNDERWEIGHT: "Underweight",
            self.NORMAL: "Normal weight",
            self.OVERWEIGHT: "Overweight (Pre-obesity)",
            self.OBESITY_I: "Obesity Class I",
            self.OBESITY_II: "Obesity Class II",
            self.OBESITY_III: "Obesity Class III (Morbid obesity)",
        }
        return names[self]

    @property
    def risks(self) -> list[str]:
        risk_map = {
            self.SEVERE_UNDERWEIGHT: [
                "Severe nutritional deficiency",
                "Immune dysfunction",
                "Organ failure risk",
            ],
            self.UNDERWEIGHT: [
                "Nutritional deficiency",
                "Osteoporosis",
                "Weakened immune system",
                "Anemia",
            ],
            self.NORMAL: ["Low risk — maintain healthy lifestyle"],
            self.OVERWEIGHT: [
                "Type 2 diabetes (increased risk)",
                "Cardiovascular disease",
                "Hypertension",
                "Dyslipidemia",
            ],
            self.OBESITY_I: [
                "Type 2 diabetes (high risk)",
                "Cardiovascular disease",
                "Sleep apnea",
                "Joint problems (osteoarthritis)",
                "Fatty liver disease",
            ],
            self.OBESITY_II: [
                "Severe cardiovascular risk",
                "Metabolic syndrome",
                "Non-alcoholic steatohepatitis (NASH)",
                "Increased surgical risk",
            ],
            self.OBESITY_III: [
                "Very high cardiovascular risk",
                "Significantly reduced life expectancy",
                "High surgical and anesthetic risk",
                "Obesity hypoventilation syndrome",
            ],
        }
        return risk_map[self]

    @classmethod
    def from_bmi(cls, bmi: float) -> "BMICategory":
        if bmi < 16.0:
            return cls.SEVERE_UNDERWEIGHT
        elif bmi < 18.5:
            return cls.UNDERWEIGHT
        elif bmi < 25.0:
            return cls.NORMAL
        elif bmi < 30.0:
            return cls.OVERWEIGHT
        elif bmi < 35.0:
            return cls.OBESITY_I
        elif bmi < 40.0:
            return cls.OBESITY_II
        else:
            return cls.OBESITY_III
