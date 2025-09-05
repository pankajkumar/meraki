import openai
from typing import Dict, Any
from src.config import OPENAI_API_KEY

class LLMAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_error(self, question_text: str, solution_text: str, bounding_box: Dict[str, float]) -> Dict[str, Any]:
        """Analyze mathematical solution for errors"""
        
        prompt = f"""
        Question: {question_text}
        Student Solution: {solution_text}
        
        Analyze the student's mathematical work and identify any errors. Focus on the area around y-coordinate {bounding_box.get('minY', 0)}.
        
        Respond with:
        1. Error description (or "No error found")
        2. Correction suggestion
        3. Helpful hint
        4. Whether solution appears complete
        
        Be specific and educational.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a mathematics tutor helping students identify and correct errors in their work."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return self._parse_analysis(content, bounding_box)
        
        except Exception as e:
            return self._default_response(str(e), bounding_box)
    
    def _parse_analysis(self, content: str, bounding_box: Dict[str, float]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        lines = content.split('\n')
        
        error = "Error analysis completed"
        correction = "Review your work carefully"
        hint = "Check your mathematical operations"
        complete = False
        
        for line in lines:
            if "error" in line.lower() and "no error" not in line.lower():
                error = line.strip()
            elif "correction" in line.lower():
                correction = line.strip()
            elif "hint" in line.lower():
                hint = line.strip()
            elif "complete" in line.lower():
                complete = "yes" in line.lower() or "true" in line.lower()
        
        return {
            "error": error,
            "correction": correction,
            "hint": hint,
            "solution_complete": complete,
            "y": (bounding_box.get("minY", 0) + bounding_box.get("maxY", 0)) / 2
        }
    
    def _default_response(self, error_msg: str, bounding_box: Dict[str, float]) -> Dict[str, Any]:
        """Default response when LLM fails"""
        return {
            "error": "Unable to analyze solution",
            "correction": "Please review your work",
            "hint": "Check your mathematical steps",
            "solution_complete": False,
            "y": (bounding_box.get("minY", 0) + bounding_box.get("maxY", 0)) / 2
        }