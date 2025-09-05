from pydantic import BaseModel
from typing import Optional, List

class BoundingBox(BaseModel):
    minX: float
    maxX: float
    minY: float
    maxY: float

class DetectErrorRequest(BaseModel):
    question_url: str
    solution_url: str
    bounding_box: BoundingBox
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    question_id: Optional[str] = None

class DetectErrorResponse(BaseModel):
    job_id: str
    y: float
    error: str
    correction: str
    hint: str
    solution_complete: bool
    contains_diagram: bool
    question_has_diagram: bool
    solution_has_diagram: bool
    llm_used: bool
    solution_lines: Optional[List[str]] = None
    llm_ocr_lines: Optional[List[str]] = None