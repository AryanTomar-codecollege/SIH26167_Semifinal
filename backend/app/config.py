import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

def integer(name, default):
    try: return int(os.getenv(name, str(default)))
    except ValueError: return default

@dataclass(frozen=True)
class Settings:
    app_host: str = os.getenv('APP_HOST', '127.0.0.1')
    app_port: int = integer('APP_PORT', 8001)
    omniroute_base_url: str = os.getenv('OMNIROUTE_BASE_URL', 'http://127.0.0.1:20128/v1').rstrip('/')
    omniroute_api_key: str = os.getenv('OMNIROUTE_API_KEY', '')
    omniroute_model: str = os.getenv('OMNIROUTE_MODEL', 'auto')
    kaggle_ngrok_url: str = os.getenv('KAGGLE_NGROK_URL', '').rstrip('/')
    request_timeout: int = integer('REQUEST_TIMEOUT', 180)
    max_files: int = integer('MAX_FILES', 3)
    cors_origins: str = os.getenv('CORS_ORIGINS', '*')
settings = Settings()
