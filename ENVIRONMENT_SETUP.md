# Configuración de Variables de Entorno

Este proyecto utiliza variables de entorno para manejar configuraciones sensibles como claves API y credenciales.

## Archivo .env

Crea un archivo `.env` en el directorio raíz del proyecto con las siguientes variables:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=tu_google_oauth_client_id_aqui
GOOGLE_OAUTH_CLIENT_SECRET=tu_google_oauth_client_secret_aqui

# Flask Configuration
FLASK_SECRET_KEY=tu_flask_secret_key_aqui
FLASK_PORT=5000

# OpenAI API Key
OPENAI_API_KEY=tu_openai_api_key_aqui

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password_de_base_de_datos
DB_NAME=nexus_db

# Other API Keys
GOOGLE_ANALYTICS_API_KEY=tu_ga_api_key_aqui
HUBSPOT_API_KEY=tu_hubspot_api_key_aqui
META_ADS_API_KEY=tu_meta_ads_api_key_aqui
NEWS_API_KEY=tu_news_api_key_aqui
PAGESPEED_API_KEY=tu_pagespeed_api_key_aqui
CLEARBIT_API_KEY=tu_clearbit_api_key_aqui
```

## Cómo obtener las credenciales

### Google OAuth
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ 
4. Ve a "Credenciales" y crea credenciales OAuth 2.0
5. Copia el Client ID y Client Secret

### OpenAI API
1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" y genera una nueva clave
4. Copia la clave API

### Otras APIs
- **Google Analytics**: Configura en Google Analytics Admin
- **HubSpot**: Obtén desde tu cuenta de HubSpot
- **Meta Ads**: Configura en Facebook Business Manager

## Seguridad

- **NUNCA** subas el archivo `.env` al repositorio
- El archivo `.env` ya está incluido en `.gitignore`
- Usa diferentes credenciales para desarrollo y producción
- Rota las claves API regularmente

## Desarrollo Local

1. Copia el archivo `.env.example` a `.env`
2. Llena las variables con tus credenciales reales
3. Ejecuta la aplicación

```bash
cp .env.example .env
# Edita .env con tus credenciales
python app.py
``` 