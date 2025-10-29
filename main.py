from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models import Client, Stadistic
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import geoip2.database
import httpx
import re

app = FastAPI()
reader = geoip2.database.Reader("GeoLite2-City.mmdb")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "PE": "America/Lima",
    "AR": "America/Argentina/Buenos_Aires",
    "CL": "America/Santiago",
    "EC": "America/Guayaquil",
    "VE": "America/Caracas",
}


@app.get("/")
async def root():
    return {"Saludo": "Hola Test"}


@app.get("/time/{country_code}")
async def time(country_code: str):
    code = country_code.upper()
    timezone = country_timezones.get(code) if None else "UTC"
    info_timezone = ZoneInfo(timezone)
    return {"time": datetime.now(info_timezone)}


def parse_user_agent(user_agent: str):
    so_match = re.search(r"\(([^)]+)\)", user_agent)
    so = so_match.group(1) if so_match else "Desconocido"

    # Navegador y versión (busca Chrome, Firefox, Safari, Edge, etc.)
    browser_match = re.search(
        r"(Chrome|Firefox|Safari|Edge|Opera|MSIE|Trident)/([\d\.]+)", user_agent
    )

    if browser_match:
        browser = browser_match.group(1)
        version = browser_match.group(2)
        if browser == "Trident":
            browser = "Internet Explorer"
        elif browser == "MSIE":
            browser = "Internet Explorer"
    else:
        browser, version = "Desconocido", "0.0"

    return browser, version, so


@app.get("/infoDevice")
async def infoDevice(request: Request):
    clientIP = request.client.host
    user_agent = request.headers.get("user-agent", "Desconocido")
    navegador, version, so = parse_user_agent(user_agent)

    data = {}

    if clientIP is None or not clientIP:
        data = {"error": "No se pudo obtener la IP del cliente"}

    elif clientIP.startswith(("10.", "192.168.", "172.")) or clientIP in (
        "127.0.0.1",
        "::1",
    ):
        data = {
            "error": "No se puede geolocalizar desde el servidor con IP local/privada"
        }

    else:
        try:
            response = reader.city(clientIP)

            country = response.country.name
            city = response.city.name
            timezone = response.location.time_zone if None else "UTC"
            info_timezone = ZoneInfo(timezone)

            data = {
                "country": country,
                "city": city,
                "timezone": timezone,
                "time": datetime.now(info_timezone),
            }
        except Exception:
            data = {"error": "IP no encontrada en la base de datos de redes"}

    if "error" not in data:
        info_stadistic = {
            "ip": clientIP,
            "navegator": navegador,
            "version": version,
            "so": so,
            "city": data["city"],
            "country": data["country"],
            "timezone": data["timezone"],
            "time": data["time"],
        }
    else:
        info_stadistic = {
            "ip": clientIP,
            "navegator": navegador,
            "version": version,
            "so": so,
            "city": "Ibarra",
            "country": "Ecuador",
            "timezone": "America/Guayaquil",
            "time": str(datetime.now(ZoneInfo("America/Guayaquil"))),
        }

    async with httpx.AsyncClient() as client:
        await client.post("http://127.0.0.1:8000/stadistic", json=info_stadistic)

    return {
        "ip": clientIP,
        "userAgent": user_agent,
        "navegator": navegador,
        "version": version,
        "so": so,
        "dataUser": data,
    }


db_clients: list[Client] = []


@app.post("/clients/", response_model=Client)
async def createClient(infoClient: Client):
    client = Client.model_validate(infoClient.model_dump())
    db_clients.append(client)
    return client


@app.get("/clients/", response_model=list[Client])
async def listClients():
    return db_clients


db_stadistics: list[Stadistic] = []


@app.post("/stadistic", response_model=Stadistic)
async def generateStadistic(infoStadistic: Stadistic):
    stadistic = Stadistic.model_validate(infoStadistic.model_dump())
    db_stadistics.append(stadistic)
    return stadistic


@app.get("/stadistics")
async def viewStadistics():
    if not db_stadistics:
        return {"message": "No hay estadísticas registradas todavía."}

    total = len(db_stadistics)

    countries = [s.country for s in db_stadistics if s.country]
    cities = [s.city for s in db_stadistics if s.city]
    navegators = [s.navegator for s in db_stadistics if s.navegator]
    systems = [s.so for s in db_stadistics if s.so]

    stats = {
        "total": total,
        "countries": dict(Counter(countries)),
        "cities": dict(Counter(cities)),
        "navegetors": dict(Counter(navegators)),
        "so": dict(Counter(systems)),
        "last_conecctions": [
            {
                "country": s.country,
                "city": s.city,
                "navegator": s.navegator,
                "so": s.so,
                "time": s.time,
            }
            for s in sorted(db_stadistics, key=lambda x: x.time, reverse=True)[:5]
        ],
    }

    try:
        hours = [datetime.fromisoformat(s.time).hour for s in db_stadistics]
        stats["activity_hour"] = dict(Counter(hours))
    except Exception:
        stats["activity_hour"] = {}

    return stats
