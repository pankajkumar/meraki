from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional
from src.models import DetectErrorRequest, DetectErrorResponse
from src.detector import ErrorDetector
from src.config import API_KEY, MAX_CONCURRENT_REQUESTS

app = FastAPI(title="Error Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = ErrorDetector()
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/detect-error", response_model=DetectErrorResponse)
async def detect_error(
    request: DetectErrorRequest,
    api_key: str = Depends(verify_api_key)
):
    """Detect errors in student mathematical solutions"""
    
    async with semaphore:  # Limit concurrent requests
        try:
            # Timeout handling
            response = await asyncio.wait_for(
                detector.detect_error(request),
                timeout=30.0
            )
            return response
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Request timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "error-detection-api"}