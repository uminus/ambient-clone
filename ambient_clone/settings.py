from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str
    db_file: Optional[str] = None
    tsdb_file: Optional[str] = None


settings = Settings()
