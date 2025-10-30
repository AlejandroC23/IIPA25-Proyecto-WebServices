from datetime import datetime
from globals import WEEKDAY, HOUR
import asyncio
import httpx
import time

from mail import enviar_correo

API_URL = "http://127.0.0.1:8000/stadistics"
RECEIVER = "alejandro.cevallos919@ist17dejulio.edu.ec"
SUBJECT = "Reporte de estadísticas - Página Web"
INTERVAL = 10  # 3600 Una hora


def generateHTML(stats: dict) -> str:
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                padding: 20px;
            }}
            h1 {{
                color: #0066cc;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #007BFF;
                color: white;
            }}
            .section {{
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Reporte de Estadísticas - {date}</h1>

        <div class="section">
            <h2>Resumen general</h2>
            <ul>
                <li><b>Total registros:</b> {stats.get("total", 0)}</li>
            </ul>
        </div>

        <div class="section">
            <h2>Por país</h2>
            {createTable(stats.get("countries", {}))}
        </div>

        <div class="section">
            <h2>Por ciudad</h2>
            {createTable(stats.get("cities", {}))}
        </div>

        <div class="section">
            <h2>Navegadores</h2>
            {createTable(stats.get("navegetors", {}))}
        </div>

        <div class="section">
            <h2>Sistemas Operativos</h2>
            {createTable(stats.get("so", {}))}
        </div>

        <div class="section">
            <h2>Actividad por hora</h2>
            {createTable(stats.get("activity_hour", {}), header=("Hora", "Conexiones"))}
        </div>

        <div class="section">
            <h2>Últimas conexiones</h2>
            {createTableConnections(stats.get("last_conecctions", []))}
        </div>
    </body>
    </html>
    """
    return html


def createTable(data: dict, header=("Elemento", "Cantidad")) -> str:
    if not data:
        return "<p>No hay datos disponibles.</p>"
    filas = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data.items())
    return f"""
    <table>
        <tr><th>{header[0]}</th><th>{header[1]}</th></tr>
        {filas}
    </table>
    """


def createTableConnections(connections: list) -> str:
    if not connections:
        return "<p>No hay conexiones recientes.</p>"
    rows = "".join(
        f"<tr><td>{c['country']}</td><td>{c['city']}</td><td>{c['navegator']}</td><td>{c['so']}</td><td>{c['time']}</td></tr>"
        for c in connections
    )
    return f"""
    <table>
        <tr><th>País</th><th>Ciudad</th><th>Navegador</th><th>SO</th><th>Hora</th></tr>
        {rows}
    </table>
    """


def awaitDateTime():
    now = datetime.now()
    return now.weekday() == WEEKDAY and now.hour == HOUR


async def service():
    send = False

    while True:
        try:
            if awaitDateTime():
                if not send:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(API_URL)
                        response.raise_for_status()
                        stats = response.json()

                        if "message" in stats:
                            print(
                                f"[{datetime.now()}] No hay datos para enviar todavía."
                            )
                            send = False
                        else:
                            body = generateHTML(stats)
                            enviar_correo(RECEIVER, SUBJECT, body)
                            print(
                                f"[{datetime.now()}] Reporte enviado con éxito a {RECEIVER}"
                            )
                            send = True

            else:
                send = False
        except Exception as e:
            print(f"[{datetime.now()}] Error al procesar reporte: {e}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    print("Servicio de estadísticas iniciado...")
    asyncio.run(service())
