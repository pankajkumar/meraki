import logging
import json
from datetime import datetime
from src.config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

class StructuredLogger:
    @staticmethod
    def log_request(job_id: str, request_data: dict):
        logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "request_received",
            "job_id": job_id,
            "request_size": len(str(request_data))
        }))
    
    @staticmethod
    def log_response(job_id: str, latency: float, success: bool):
        logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "request_completed",
            "job_id": job_id,
            "latency_ms": latency * 1000,
            "success": success
        }))
    
    @staticmethod
    def log_error(job_id: str, error: str):
        logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "error",
            "job_id": job_id,
            "error": error
        }))