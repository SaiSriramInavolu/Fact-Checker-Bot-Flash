import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 2048))

    SEARCH_TOOL: str = os.getenv("SEARCH_TOOL", "duckduckgo")

settings = Settings()
