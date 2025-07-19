import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
from models.entities.User import User

load_dotenv()

db = SQLAlchemy()

def get_user_preferred_language(user_id):
    """
    Obtiene el idioma preferido del usuario desde la base de datos.
    """
    user = User.query.get(user_id)
    return user.preferred_language if user else None

def update_user_preferred_language(user_id, language):
    """
    Actualiza el idioma preferido del usuario en la base de datos.
    """
    user = User.query.get(user_id)
    if user:
        user.preferred_language = language
        db.session.commit()

def save_or_update_user(email, **kwargs):
    """
    Crea o actualiza un usuario en la base de datos utilizando SQLAlchemy.
    """
    user = User.query.filter_by(email=email).first()
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
    else:
        user = User(email=email, **kwargs)
        db.session.add(user)
    db.session.commit()
    return user.id

def save_sensitive_data(user_id, **kwargs):
    """
    Guarda o actualiza datos sensibles de un usuario.
    """
    # Esta función necesita ser implementada con un modelo para datos sensibles
    pass

def get_sensitive_data(user_id):
    """
    Obtiene datos sensibles de un usuario.
    """
    # Esta función necesita ser implementada con un modelo para datos sensibles
    pass

def save_login_activity(user_id, ip_address, display_name):
    """
    Guarda la actividad de inicio de sesión de un usuario.
    """
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.now()
        # Aquí se necesitaría un modelo para la actividad de login
        db.session.commit()

def update_logout_activity(user_id):
    """
    Actualiza la actividad de cierre de sesión de un usuario.
    """
    # Aquí se necesitaría un modelo para la actividad de login
    pass

def save_interaction(user_id, interaction_type, input_data, output_data):
    """
    Guarda una interacción del usuario.
    """
    # Aquí se necesitaría un modelo para las interacciones
    pass

def save_conversation(user_id, display_name, user_message, assistant_response):
    """
    Guarda una conversación de chat.
    """
    # Aquí se necesitaría un modelo para las conversaciones
    pass

def save_tokens_to_db(email, access_token, refresh_token):
    """
    Guarda los tokens de acceso y refresco de un usuario.
    """
    user = User.query.filter_by(email=email).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        db.session.commit()

def save_web_analysis(user_id, url, scraped_data, analysis_summary):
    """
    Guarda un análisis web.
    """
    # Aquí se necesitaría un modelo para los análisis web
    pass

def save_calculator_results(user_id, metric_type, **kwargs):
    """
    Guarda los resultados de la calculadora.
    """
    # Aquí se necesitaría un modelo para los resultados de la calculadora
    pass

def save_business_idea(user_id, **kwargs):
    """
    Guarda una idea de negocio.
    """
    # Aquí se necesitaría un modelo para las ideas de negocio
    pass

def save_marketing_strategy(user_id, **kwargs):
    """
    Guarda una estrategia de marketing.
    """
    # Aquí se necesitaría un modelo para las estrategias de marketing
    pass

def save_funnel_analysis(user_id, **kwargs):
    """
    Guarda un análisis de embudo.
    """
    # Aquí se necesitaría un modelo para los análisis de embudo
    pass

def save_hubspot_data(user_id, **kwargs):
    """
    Guarda datos de HubSpot.
    """
    # Aquí se necesitaría un modelo para los datos de HubSpot
    pass

def get_hubspot_data(user_id):
    """
    Obtiene datos de HubSpot.
    """
    # Aquí se necesitaría un modelo para los datos de HubSpot
    pass

def check_user_credits(user_id, required_credits):
    """
    Verifica si un usuario tiene suficientes créditos.
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuario no encontrado."
    
    # Lógica de feedback_submitted necesita ser implementada
    feedback_submitted = False

    if user.credits <= 0.9 and not feedback_submitted:
        return False, "Mostrar Feedback"
    if user.credits < required_credits:
        return False, "Créditos insuficientes."
    
    return True, user.credits

def save_feedback(user_id, rating, ease_of_use, comment):
    """
    Guarda el feedback de un usuario.
    """
    # Aquí se necesitaría un modelo para el feedback
    pass

def update_feedback_status(user_id):
    """
    Actualiza el estado de feedback de un usuario.
    """
    # Esta lógica debería estar en el modelo de usuario o feedback
    pass

def save_search_console_data(user_id, site_url, start_date, end_date, summary):
    """
    Guarda datos de Search Console.
    """
    # Aquí se necesitaría un modelo para los datos de Search Console
    pass

def get_user_credits(user_id):
    """
    Obtiene los créditos de un usuario.
    """
    user = User.query.get(user_id)
    return user.credits if user else None

def record_transaction(user_id, payment_id, payer_id, amount, credits, status="completed"):
    """
    Registra una transacción.
    """
    # Aquí se necesitaría un modelo para las transacciones
    pass

def get_user_id_from_payment(payment_id):
    """
    Obtiene el ID de un usuario a partir de un ID de pago.
    """
    # Aquí se necesitaría un modelo para las transacciones
    pass

def get_user_history(user_id):
    """
    Obtiene el historial de un usuario.
    """
    # Esta función necesitaría consultar varios modelos
    pass

def get_user(user_id):
    """
    Obtiene un usuario por su ID.
    """
    return User.query.get(user_id)

def create_user(email, password, **kwargs):
    """
    Crea un nuevo usuario.
    """
    user = User(email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user.id

def update_user(user_id, **kwargs):
    """
    Actualiza un usuario.
    """
    user = User.query.get(user_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.session.commit()

def get_user_by_email(email):
    """
    Obtiene un usuario por su email.
    """
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    """
    Obtiene un usuario por su nombre de usuario.
    """
    return User.query.filter_by(display_name=username).first()

def update_user_credits(user_id, credits_change):
    """
    Actualiza los créditos de un usuario.
    """
    user = User.query.get(user_id)
    if user:
        user.credits += credits_change
        db.session.commit()

def ping_database():
    """
    Hace ping a la base de datos para mantener la conexión activa.
    """
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception as e:
        print(f"[WARNING] Error al hacer ping a la base de datos: {str(e)}")
        return False

class DatabaseConnection:
    """
    Gestor de contexto para manejar conexiones a la base de datos.
    Garantiza que las conexiones se cierren correctamente incluso si hay excepciones.
    """
    def __init__(self, mysql, dictionary=False):
        self.mysql = mysql
        self.cursor = None
        self.dictionary = dictionary
    
    def __enter__(self):
        try:
            if self.dictionary:
                import MySQLdb
                self.cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            else:
                self.cursor = self.mysql.connection.cursor()
            return self.cursor
        except Exception as e:
            print(f"[ERROR] Error al obtener cursor: {str(e)}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.mysql.connection.rollback()
            else:
                self.mysql.connection.commit()
            
            if self.cursor:
                self.cursor.close()
                
            return False
        except Exception as e:
            print(f"[ERROR] Error al cerrar cursor/conexión: {str(e)}")
            return False

def save_ga_property(user_id, property_id, name, description=None):
    """
    Guarda una propiedad de Google Analytics 4 para un usuario.
    """
    # Aquí se necesitaría un modelo para las propiedades de GA4
    pass