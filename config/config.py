"""Global configuration for the Evidence-Based AI Research Agent."""
import os
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        pass

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
DATABASE_PATH = DATA_DIR / "sample_database.sqlite"
BENCHMARK_PATH = DATA_DIR / "evaluation_benchmark.json"

class Settings:
    DATABASE_PATH: Path = DATABASE_PATH
    DOCS_DIR: Path = DOCS_DIR
    BENCHMARK_PATH: Path = BENCHMARK_PATH
    
    # Environment & Provider settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # 'mock', 'openai', 'anthropic', 'gemini'
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Models
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # Retrieval Configuration
    TOP_K_RETRIEVAL: int = 5
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60
    
    # Safety & Reliability Sandbox
    SQL_MAX_ROWS: int = 500
    SQL_TIMEOUT_SECONDS: float = 4.0
    SQL_ALLOWED_TABLES: list[str] = [
        "monthly_revenue",
        "regional_sales",
        "product_catalog",
        "orders",
        "customer_churn",
        "marketing_spend",
        "supply_chain_incidents",
        "cost_of_goods"
    ]
    
    # Verification & Reflection
    MAX_VERIFICATION_LOOPS: int = 3
    MIN_GROUNDEDNESS_THRESHOLD: float = 0.85
    MIN_CITATION_CONFIDENCE: float = 0.80

settings = Settings()
