
import os
import pickle

HUBSPOT_TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'hubspot_token.pickle')

def get_hubspot_access_token() -> str:
    """
    Obtiene el token de acceso de HubSpot. Si no está guardado localmente,
    solicita al usuario que lo introduzca.

    Returns:
        El token de acceso de HubSpot.
    """
    if os.path.exists(HUBSPOT_TOKEN_FILE):
        with open(HUBSPOT_TOKEN_FILE, 'rb') as token_file:
            access_token = pickle.load(token_file)
    else:
        access_token = input("Por favor, introduce tu token de acceso de HubSpot Private App: ")
        with open(HUBSPOT_TOKEN_FILE, 'wb') as token_file:
            pickle.dump(access_token, token_file)
            
    return access_token

if __name__ == '__main__':
    print("Obteniendo el token de acceso de HubSpot...")
    token = get_hubspot_access_token()
    print("¡Token de HubSpot obtenido con éxito!")
    print(f"Token guardado en: {HUBSPOT_TOKEN_FILE}")
