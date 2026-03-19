import re


def parse_bmi(text: str) -> float | None:
    m = re.search(r"BMI:\s*([\d.]+)", text)
    return float(m.group(1)) if m else None


def parse_icd10(text: str) -> list[dict]:
    results = []
    for line in text.split("\n"):
        m = re.match(r"\s+([A-Z]\d[\w.]*): (.+?)(?:\s*\(confidence: (\w+)\))?$", line)
        if m:
            results.append(
                {
                    "Code": m.group(1),
                    "Description": m.group(2).strip(),
                    "Confidence": m.group(3) or "",
                }
            )
    return results
