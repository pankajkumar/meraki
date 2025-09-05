import uuid
import time
from typing import Dict, Any
from src.models import DetectErrorRequest, DetectErrorResponse
from src.ocr import OCRProcessor
from src.llm import LLMAnalyzer
from src.storage import SimpleStorage
from src.logging import StructuredLogger

class ErrorDetector:
    def __init__(self):
        self.ocr = OCRProcessor()
        self.llm = LLMAnalyzer()
        self.storage = SimpleStorage()
        self.logger = StructuredLogger()
    
    async def detect_error(self, request: DetectErrorRequest) -> DetectErrorResponse:
        """Main error detection pipeline"""
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.logger.log_request(job_id, request.dict())
            
            # Extract text from images
            question_lines = self.ocr.extract_text_from_url(request.question_url)
            solution_lines = self.ocr.extract_text_from_url(request.solution_url)
            
            # Check for diagrams
            question_has_diagram = self.ocr.has_diagram(request.question_url)
            solution_has_diagram = self.ocr.has_diagram(request.solution_url)
            
            # Analyze for errors
            question_text = " ".join(question_lines)
            solution_text = " ".join(solution_lines)
            
            analysis = self.llm.analyze_error(
                question_text, 
                solution_text, 
                request.bounding_box.dict()
            )
            
            # Build response
            response = DetectErrorResponse(
                job_id=job_id,
                y=analysis["y"],
                error=analysis["error"],
                correction=analysis["correction"],
                hint=analysis["hint"],
                solution_complete=analysis["solution_complete"],
                contains_diagram=question_has_diagram or solution_has_diagram,
                question_has_diagram=question_has_diagram,
                solution_has_diagram=solution_has_diagram,
                llm_used=True,
                solution_lines=solution_lines,
                llm_ocr_lines=question_lines + solution_lines
            )
            
            # Store for auditing
            self.storage.save_request_response(
                job_id, 
                request.dict(), 
                response.dict()
            )
            
            latency = time.time() - start_time
            self.logger.log_response(job_id, latency, True)
            
            return response
            
        except Exception as e:
            self.logger.log_error(job_id, str(e))
            latency = time.time() - start_time
            self.logger.log_response(job_id, latency, False)
            
            # Return partial result instead of failing
            return DetectErrorResponse(
                job_id=job_id,
                y=request.bounding_box.minY,
                error="Processing error occurred",
                correction="Please try again",
                hint="Check your input and try again",
                solution_complete=False,
                contains_diagram=False,
                question_has_diagram=False,
                solution_has_diagram=False,
                llm_used=False
            )