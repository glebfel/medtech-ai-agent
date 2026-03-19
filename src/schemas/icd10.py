from pydantic import BaseModel


class ICD10SearchResult(BaseModel):
    code: str
    description: str
    similarity: float = 0.0

    @property
    def confidence(self) -> str:
        if self.similarity >= 0.4:
            return "high"
        if self.similarity >= 0.2:
            return "medium"
        return "low"

    def format(self) -> str:
        return f"  {self.code}: {self.description} (confidence: {self.confidence})"
