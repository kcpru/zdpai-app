from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_key: str
    jwt_issuer: str
    jwt_audience: str
    jwt_expires_minutes: int = 120
    cors_origins: str = ""
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1/"
    random_avatars_base_url: str = "https://api.dicebear.com/9.x/"
    files_root: str = "."

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
