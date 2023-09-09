from datetime import datetime

from pydantic import BaseModel, Extra


class Datum(BaseModel):
    timestamp: datetime

    class Config:
        extra = Extra.allow
