from cryptography.fernet import Fernet

# Generar una clave de cifrado
def generar_clave_cifrado():
    return Fernet.generate_key()

# Cifrar datos sensibles
def cifrar_datos(clave, datos):
    f = Fernet(clave)
    return f.encrypt(datos.encode())

# Descifrar datos sensibles
def descifrar_datos(clave, datos_cifrados):
    f = Fernet(clave)
    return f.decrypt(datos_cifrados).decode()
