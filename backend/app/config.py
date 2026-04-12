from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://pimp:pimp@localhost:5432/pimp"
    AI_PROVIDER: str = "fake"  # "anthropic" | "openai" | "fake"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    PIMP_RUN_LIVE_AI: int = 0

    # Scheduling defaults
    DEFAULT_INTERVAL_MIN: int = 30
    MIN_INTERVAL_MIN: int = 10
    MAX_INTERVAL_MIN: int = 72 * 60  # 72 hours


settings = Settings()
