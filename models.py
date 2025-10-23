from pydantic import BaseModel


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
    time: str | None


class GenerateStadistic(Stadistic):
    pass
