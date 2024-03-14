from functools import lru_cache
from typing import TypeAlias

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings):
    app_name: str = "Memoire AI"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    OPENAI_API_KEY: str


@lru_cache
def get_settings():
    return Settings()


AnnotatedSettings: TypeAlias = Annotated[Settings, Depends(get_settings)]
