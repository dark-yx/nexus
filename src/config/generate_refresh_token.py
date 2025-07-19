from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Define el archivo de credenciales descargado desde Google Cloud Console
CLIENT_SECRETS_FILE = "client_secret.json"  # Ruta al archivo .json

# Definir el alcance de acceso necesario para Google Ads
SCOPES = [
    "https://www.googleapis.com/auth/adwords"          # Google Search Console
]


# Configuración de flujo de OAuth 2.0
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

# Ejecutar el flujo de OAuth y obtener las credenciales
credentials = flow.run_local_server(port=0)

# Imprimir el refresh token
print(f"Refresh Token: {credentials.refresh_token}")

# Puedes guardar las credenciales en un archivo si lo deseas
# with open("google_ads_credentials.json", "w") as token:
#     token.write(credentials.to_json())
