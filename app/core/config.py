from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Todo API"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_database: str = "todo_api"
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    rate_limit_requests: int = Field(default=120, ge=1)
    auth_rate_limit_requests: int = Field(default=10, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
