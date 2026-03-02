from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All config comes from environment variables (or .env file locally).
    On Render: set DATABASE_URL in the service's Environment tab.
    """

    database_url: str = "postgresql://factory:factory@localhost:5432/factory_db"

    # Connection pool tuning (sensible defaults for Render free tier)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True   # drops stale connections automatically

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()