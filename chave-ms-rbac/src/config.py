from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "chave_rbac"
    db_user: str = "rbac"
    db_password: str = "rbac_secret"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
