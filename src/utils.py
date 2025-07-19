from db import get_user_preferred_language

def get_language_context(db, user_id):
    """
    Obtiene el contexto de idioma para un usuario, incluyendo el código de idioma y su nombre.
    Retorna un diccionario con 'code' y 'name'.
    """
    # Obtener el idioma preferido del usuario
    preferred_language = get_user_preferred_language(db, user_id)
    if not preferred_language:
        preferred_language = 'en'  # Default to English

    # Mapear el código de idioma a un nombre legible
    language_names = {
        "en": "English",
        "es": "Spanish",
        "pt": "Portuguese",
        "fr": "French"
    }
    lang_name = language_names.get(preferred_language, "English")

    return {
        'code': preferred_language,
        'name': lang_name
    }

def get_user_display_name(db, user_id):
    """
    Obtiene el nombre de visualización del usuario.
    """
    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT display_name FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else "User"
    except Exception:
        return "User"

def get_base_system_message(display_name, lang_name):
    """
    Retorna el mensaje base del sistema con el nombre del usuario y el idioma preferido.
    """
    return (
        "My name is DEREK, and I am a virtual digital marketing consultant. I was developed in the Digital R&D laboratory. "
        "I specialize in marketing, product development, and online sales strategies. I will answer questions as an expert in Digital Marketing, "
        "Growth Hacking, Branding, SEO, PPC, Social Media, CRO, Neuromarketing, and web traffic generation. My priority is to help companies "
        "increase the ROI of their websites, mobile applications, and digital strategies. I was initially programmed by Jonnathan Peña as part of the "
        "Nexus Metrics project 'An AI-powered Unified Marketing Platform', which was conceived on January 2, 2024. For more information about the company, "
        "our current research projects, and to hire Weblifetech's services, please contact marketing@weblifetech.com, call +593982541659, or visit weblifetech.com. "
        "You must provide short answers. Also, please note that the user's name is {} and they prefer that all responses be in {}. Please, always respond in {}."
    ).format(display_name, lang_name, lang_name) 