import os
from dotenv import load_dotenv

load_dotenv()

# 간단한 설정 클래스
class Settings:
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()