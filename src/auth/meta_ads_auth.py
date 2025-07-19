
import os
import pickle

META_ADS_CREDS_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'meta_ads_creds.pickle')

def get_meta_ads_credentials() -> dict:
    """
    Obtiene las credenciales de la API de Meta Ads. Si no están guardadas localmente,
    solicita al usuario que las introduzca.

    Returns:
        Un diccionario con las credenciales de Meta Ads (app_id, app_secret, access_token).
    """
    if os.path.exists(META_ADS_CREDS_FILE):
        with open(META_ADS_CREDS_FILE, 'rb') as creds_file:
            credentials = pickle.load(creds_file)
    else:
        app_id = input("Por favor, introduce tu Meta App ID: ")
        app_secret = input("Por favor, introduce tu Meta App Secret: ")
        access_token = input("Por favor, introduce tu Meta Access Token: ")
        credentials = {
            "app_id": app_id,
            "app_secret": app_secret,
            "access_token": access_token,
        }
        with open(META_ADS_CREDS_FILE, 'wb') as creds_file:
            pickle.dump(credentials, creds_file)
            
    return credentials

if __name__ == '__main__':
    print("Obteniendo las credenciales de Meta Ads...")
    creds = get_meta_ads_credentials()
    print("¡Credenciales de Meta Ads obtenidas con éxito!")
    print(f"Credenciales guardadas en: {META_ADS_CREDS_FILE}")
