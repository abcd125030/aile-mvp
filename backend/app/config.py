from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    LLM_PROVIDER: str = "qwen"
    LLM_MODEL: str = "qwen-plus"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_API_KEY: str = ""
    LLM_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
