from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
