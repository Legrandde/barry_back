from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SECRET_KEY = "change-me-in-production-please-use-a-long-random-key"
DEFAULT_ADMIN_PASSWORD = "admin1234"


class Settings(BaseSettings):
    """Configuration chargée depuis les variables d'environnement (ou le fichier .env)."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Alhassane Barry — Portfolio CMS API"
    environment: str = "development"

    database_url: str = f"sqlite:///{(BASE_DIR / 'cms.db').as_posix()}"

    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    # Compte admin créé au premier démarrage s'il n'existe aucun admin
    admin_username: str = "admin"
    admin_password: str = DEFAULT_ADMIN_PASSWORD

    # Origines autorisées, séparées par des virgules dans le .env
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    media_dir: Path = BASE_DIR / "media"
    media_url_path: str = "/media"
    # URL publique de l'API (ex: https://api.barryalhassane.com) pour construire les liens des médias.
    # Si vide, l'URL de la requête est utilisée.
    public_base_url: str | None = None
    max_upload_size_mb: int = 20

    # Vidéos : taille max à l'envoi, puis compression automatique au-delà du seuil
    max_video_upload_size_mb: int = 300
    video_compression_threshold_mb: float = 15
    video_max_dimension: int = 720  # plus petit côté, en pixels (720p)
    video_crf: int = 28  # qualité H.264 : plus haut = plus léger
    video_compression_timeout_seconds: int = 1800
    # Chemin de ffmpeg ; par défaut celui du système, sinon celui fourni par imageio-ffmpeg
    ffmpeg_path: str | None = None

    # Durée de conservation des statistiques de visite
    analytics_retention_days: int = 395
    # Base locale DB-IP City Lite pour déduire pays/région/ville sans jamais stocker ni envoyer d'IP
    geoip_db_path: Path = BASE_DIR / "data" / "dbip-city-lite.mmdb"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Accepte les URLs Render/Railway (postgres:// ou postgresql://) avec le driver psycopg3."""
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return "postgresql+psycopg://" + value.removeprefix("postgres://")
            if value.startswith("postgresql://"):
                return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def insecure_defaults(self) -> list[str]:
        problems = []
        if self.secret_key in (DEFAULT_SECRET_KEY, "change-me"):
            problems.append("SECRET_KEY")
        if self.admin_password in (DEFAULT_ADMIN_PASSWORD, "change-me"):
            problems.append("ADMIN_PASSWORD")
        return problems


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
