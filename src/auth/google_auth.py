
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define los scopes necesarios para todas las APIs de Google que vamos a utilizar.
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/bigquery'
]

# Ubicación del archivo de secretos del cliente y del token de usuario.
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'client_secret.json')
TOKEN_PICKLE_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.pickle')

def get_google_credentials() -> Credentials:
    """
    Obtiene las credenciales de usuario de Google. Si no existen o han expirado,
    inicia el flujo de autenticación OAuth 2.0 para obtenerlas.

    Returns:
        Un objeto de credenciales de Google (google.oauth2.credentials.Credentials).
    """
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"El archivo de secretos del cliente no se encontró en: {CLIENT_SECRETS_FILE}. "
                    f"Por favor, descárgalo desde la Google Cloud Console y guárdalo en esa ubicación."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

if __name__ == '__main__':
    # Este bloque de código se puede ejecutar para iniciar el flujo de autenticación
    # por primera vez y generar el archivo token.pickle.
    print("Iniciando el proceso de autenticación de Google...")
    credentials = get_google_credentials()
    print("¡Autenticación completada con éxito!")
    print(f"Token guardado en: {TOKEN_PICKLE_FILE}")
