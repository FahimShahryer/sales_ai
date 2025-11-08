"""
Application Settings
Loads configuration from environment variables
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # "gemini" or "openai"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3  # Increased slightly for better format following
    LLM_MAX_TOKENS: int = 8000  # Increased from 2000 to handle larger synthesis prompts

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_PATH: Path = PROJECT_ROOT / "data"
    FAISS_INDEX_PATH: Path = DATA_PATH / "faiss_index"
    SALES_DATA_PATH: Path = DATA_PATH / "sales_transactions.csv"

    # RAG Configuration
    RAG_TOP_K: int = 5
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Code Execution Security
    ALLOWED_PANDAS_OPERATIONS: list = [
        "read_csv", "groupby", "sum", "mean", "count", "sort_values",
        "head", "tail", "describe", "value_counts", "merge", "filter",
        "loc", "iloc", "query", "agg", "pivot_table"
    ]

    # API Configuration
    API_TITLE: str = "Akij Sales Intelligence API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Multi-Agent Sales Intelligence System with RAG"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
