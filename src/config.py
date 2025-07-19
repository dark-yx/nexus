import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY')
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}

developer_token = os.getenv('DEVELOPER_TOKEN')

credit_plans = {
    "Test": {"amount": 10.00, "credits": 50, "descripcion": "50 credit trial package"},
    "Starter": {"amount": 250.00, "credits": 1400, "descripcion": "1400 credits starter pack"},
    "Plus": {"amount": 500.00, "credits": 3200, "descripcion": "3200 credits plus package"},
    "Growth": {"amount": 850.00, "credits": 5400, "descripcion": "5400 credits growth pack"}
}

 
