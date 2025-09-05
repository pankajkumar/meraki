import asyncio
import json
from src.detector import ErrorDetector
from src.models import DetectErrorRequest, BoundingBox

async def run_demo():
    """Run a simple demo of the error detection API"""
    print("Error Detection API Demo")
    print("=" * 30)
    
    detector = ErrorDetector()
    
    # Sample request
    sample_request = DetectErrorRequest(
        question_url="https://i.ibb.co/BH6zN37D/Q1.jpg",
        solution_url="https://i.ibb.co/fzm0b6TZ/Attempt1.jpg",
        bounding_box=BoundingBox(minX=100, maxX=300, minY=50, maxY=100),
        question_id="demo_question"
    )
    
    print("Processing sample request...")
    print(f"Question URL: {sample_request.question_url}")
    print(f"Solution URL: {sample_request.solution_url}")
    
    try:
        response = await detector.detect_error(sample_request)
        
        print("\nResponse:")
        print(f"Job ID: {response.job_id}")
        print(f"Error: {response.error}")
        print(f"Correction: {response.correction}")
        print(f"Hint: {response.hint}")
        print(f"Solution Complete: {response.solution_complete}")
        print(f"LLM Used: {response.llm_used}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_demo())