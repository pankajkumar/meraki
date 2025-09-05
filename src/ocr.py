import requests
from PIL import Image
from io import BytesIO
from typing import List, Tuple
import openai
from src.config import OPENAI_API_KEY

class OCRProcessor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def extract_text_from_url(self, image_url: str) -> List[str]:
        """Extract text from image URL using OpenAI Vision API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all mathematical text and equations from this image. Return each line separately."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }],
                max_tokens=500
            )
            
            text = response.choices[0].message.content
            return [line.strip() for line in text.split('\n') if line.strip()]
        
        except Exception as e:
            print(f"OCR error: {e}")
            return []
    
    def has_diagram(self, image_url: str) -> bool:
        """Check if image contains diagrams/graphs"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Does this image contain any diagrams, graphs, or geometric figures? Answer only 'yes' or 'no'."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }],
                max_tokens=10
            )
            
            return response.choices[0].message.content.lower().strip() == "yes"
        
        except Exception:
            return False