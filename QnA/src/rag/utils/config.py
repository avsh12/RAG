from pathlib import Path
from uuid import UUID

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    # Databases
    SQL_AUTH_DB_PATH: Path
    OBJ_FILE_DB_PATH: Path
    VECTOR_DB_PATH: Path

    # Models Paths
    EMBEDDING_MODEL_PATH: str
    LLM_MODEL_PATH: str

    EMBEDDING_DIM: int

    ID_NAMESPACE: UUID

    COLLECTION_NAME: str

    MAX_FILE_SIZE_BYTES: int

    @field_validator(
        "SQL_AUTH_DB_PATH", "OBJ_FILE_DB_PATH", "VECTOR_DB_PATH", mode="before"
    )
    def resolve_absolute_path(cls, value: str) -> Path:
        path = Path(value)

        if not path.is_absolute():
            return ROOT / path
        return path

    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")


settings = Settings()


# print(settings.model_dump())
