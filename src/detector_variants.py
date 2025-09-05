import uuid
import time
from typing import Dict, Any
from src.models import DetectErrorRequest, DetectErrorResponse
from src.ocr import OCRProcessor
from src.storage import SimpleStorage
from src.logging import StructuredLogger
import openai
from src.config import OPENAI_API_KEY

class BaselineDetector:
    """Baseline: Simple OCR + basic LLM prompt"""
    def __init__(self):
        self.ocr = OCRProcessor()
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.storage = SimpleStorage()
        self.logger = StructuredLogger()
    
    async def detect_error(self, request: DetectErrorRequest) -> DetectErrorResponse:
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Basic OCR
            solution_lines = self.ocr.extract_text_from_url(request.solution_url)
            solution_text = " ".join(solution_lines)
            
            # Simple LLM analysis
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Check this math solution for errors: {solution_text}"}],
                max_tokens=100,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            return DetectErrorResponse(
                job_id=job_id,
                y=request.bounding_box.minY,
                error=content[:100] if content else "No analysis",
                correction="Check your work",
                hint="Review calculations",
                solution_complete=False,
                contains_diagram=False,
                question_has_diagram=False,
                solution_has_diagram=False,
                llm_used=True,
                solution_lines=solution_lines
            )
            
        except Exception as e:
            return DetectErrorResponse(
                job_id=job_id,
                y=request.bounding_box.minY,
                error="Processing failed",
                correction="Try again",
                hint="Check input",
                solution_complete=False,
                contains_diagram=False,
                question_has_diagram=False,
                solution_has_diagram=False,
                llm_used=False
            )

class ImprovedDetector:
    """Improved: Enhanced prompting + context + structured analysis"""
    def __init__(self):
        self.ocr = OCRProcessor()
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.storage = SimpleStorage()
        self.logger = StructuredLogger()
    
    async def detect_error(self, request: DetectErrorRequest) -> DetectErrorResponse:
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Enhanced OCR with context
            question_lines = self.ocr.extract_text_from_url(request.question_url)
            solution_lines = self.ocr.extract_text_from_url(request.solution_url)
            
            question_text = " ".join(question_lines)
            solution_text = " ".join(solution_lines)
            
            # Structured prompt with examples
            prompt = f"""
            As a math tutor, analyze this student's work step by step:
            
            QUESTION: {question_text}
            STUDENT SOLUTION: {solution_text}
            
            Check for these common error types:
            1. Arithmetic mistakes (wrong calculations)
            2. Algebraic errors (incorrect operations)
            3. Conceptual misunderstandings
            4. Sign errors
            5. Missing steps
            
            Respond in this format:
            ERROR: [specific error or "No error found"]
            CORRECTION: [how to fix it]
            HINT: [educational guidance]
            COMPLETE: [yes/no if solution is finished]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert mathematics tutor focused on identifying and explaining errors in student work."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            analysis = self._parse_structured_response(content)
            
            return DetectErrorResponse(
                job_id=job_id,
                y=(request.bounding_box.minY + request.bounding_box.maxY) / 2,
                error=analysis["error"],
                correction=analysis["correction"],
                hint=analysis["hint"],
                solution_complete=analysis["complete"],
                contains_diagram=len(question_lines) > 3,  # Simple heuristic
                question_has_diagram=False,
                solution_has_diagram=False,
                llm_used=True,
                solution_lines=solution_lines,
                llm_ocr_lines=question_lines + solution_lines
            )
            
        except Exception as e:
            return DetectErrorResponse(
                job_id=job_id,
                y=request.bounding_box.minY,
                error="Analysis error occurred",
                correction="Please review your work",
                hint="Check each step carefully",
                solution_complete=False,
                contains_diagram=False,
                question_has_diagram=False,
                solution_has_diagram=False,
                llm_used=False
            )
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse structured LLM response"""
        lines = content.split('\n')
        result = {
            "error": "Error analysis completed",
            "correction": "Review your work",
            "hint": "Check your steps",
            "complete": False
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith("ERROR:"):
                result["error"] = line[6:].strip()
            elif line.startswith("CORRECTION:"):
                result["correction"] = line[11:].strip()
            elif line.startswith("HINT:"):
                result["hint"] = line[5:].strip()
            elif line.startswith("COMPLETE:"):
                result["complete"] = "yes" in line.lower()
        
        return result