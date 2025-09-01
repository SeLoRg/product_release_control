from pydantic_settings import SettingsConfigDict
from .Postgres import Postgres


class Settings(Postgres):
    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
