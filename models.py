from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class Client(BaseModel):
    name: str
    lastname: str
    identification: str
    birth_year: str


class CreateClient(Client):
    pass


class Stadistic(BaseModel):
    ip: str
    navegator: str
    version: str
    so: str
    city: str | None
    country: str | None
    timezone: str | None
    time: str = datetime.now().isoformat()


class GenerateStadistic(Stadistic):
    pass


class DateRange(BaseModel):
    date_start: date
    date_end: date

    @field_validator("date_end")
    def validateDateEnd(cls, v, info):
        if "date_start" in info.data and v < info.data["date_start"]:
            raise ValueError(
                "La fecha final debe ser igual o posterior a la fecha inicial"
            )
        return v
