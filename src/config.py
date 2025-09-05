import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = os.getenv("API_KEY", "default-key")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 30