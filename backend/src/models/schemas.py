from pydantic import BaseModel
from typing import List, Dict

class TriageInput(BaseModel):
    symptoms: List[str]
    vitals: Dict[str, str | int]
    age: int
