"""
Application configuration settings.
"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "ComplianceAgent"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql://compliance_user:compliance_pass@localhost:5432/compliance_db"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600  # 1 hour
    redis_max_connections: int = 50

    # ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8001
    chromadb_collection_name: str = "compliance_docs"

    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_device: str = "cpu"  # or "cuda" if GPU available
    embedding_batch_size: int = 32

    # Document Processing
    max_file_size_mb: int = 100
    chunk_size: int = 512
    chunk_overlap: int = 128
    supported_formats: list[str] = ["pdf", "docx", "md", "txt"]

    # Model API
    default_model: str = "qwen"
    model_timeout: int = 30
    model_max_retries: int = 3

    # Qwen Model (Enterprise Internal)
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "http://localhost:8000/v1"
    qwen_model_name: str = "qwen-plus"

    # ChatGLM Model (Enterprise Internal)
    chatglm_api_key: Optional[str] = None
    chatglm_base_url: str = "http://localhost:8001/v1"
    chatglm_model_name: str = "chatglm3"

    # Tongyi Qianwen (Alibaba Cloud)
    tongyi_api_key: Optional[str] = None
    tongyi_model_name: str = "qwen-plus"

    # Wenxin Yiyan (Baidu)
    wenxin_api_key: Optional[str] = None
    wenxin_secret_key: Optional[str] = None
    wenxin_model_name: str = "ernie-bot-4"

    # OpenAI (Optional)
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model_name: str = "gpt-4"

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000

    # Agent Configuration
    agent_max_steps: int = 10
    agent_timeout_seconds: int = 300
    agent_quality_threshold: float = 0.8

    # MCP Tool Gateway
    mcp_timeout_seconds: int = 30
    mcp_max_retries: int = 3
    mcp_backoff_multiplier: int = 2

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    src_dir: Path = base_dir / "src"
    config_dir: Path = base_dir / "config"
    logs_dir: Path = base_dir / "logs"
    data_dir: Path = base_dir / "data"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
