import mysql.connector

acceso_bd = {"host": "loalhost",
             "user" : "root",
             "password" : "clave-db",
             "database" : "nombre-db"

}


class BaseDatos:
    def __init__(self, **kwargs):
        self.conector = mysql.connect(**kwargs)
    
    def consulta(self, sql):
        cursor = self.conector.cursor()
        cursor.execute(sql)
        return cursor
    