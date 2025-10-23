import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Scopes necesarios para enviar correos
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def autenticar_gmail():
    creds = None
    # El archivo token.pickle guarda el acceso de usuario
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # Si no hay credenciales válidas, pide autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        # Guarda el acceso para la próxima vez
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    service = build("gmail", "v1", credentials=creds)
    return service


def crear_mensaje(destinatario, asunto, cuerpo):
    mensaje = MIMEText(cuerpo)
    mensaje["to"] = destinatario
    mensaje["subject"] = asunto
    mensaje_bytes = mensaje.as_bytes()
    mensaje_base64 = base64.urlsafe_b64encode(mensaje_bytes).decode()
    return {"raw": mensaje_base64}


def enviar_correo(destinatario, asunto, cuerpo):
    service = autenticar_gmail()
    mensaje = crear_mensaje(destinatario, asunto, cuerpo)
    enviado = service.users().messages().send(userId="me", body=mensaje).execute()
    print(f"Correo enviado, ID: {enviado['id']}")


# Ejemplo de uso:
destinatario = "trexmrtop23@gmail.com"
asunto = "Prueba desde API Gmail"
cuerpo = "Este es un mensaje enviado usando la API de Gmail con Python. Estamos con los guaguas de 5to"

enviar_correo(destinatario, asunto, cuerpo)
