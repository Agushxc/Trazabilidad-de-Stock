import sqlite3
from a_00_config import *

db_file = "base_de_datos_interna.db"

class DB:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def conectar(self):
        if self.conn is None:
            self.conn = sqlite3.connect(db_file)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        return self.conn

    def ejecutar(self, query, params=()):
        if self.conn is None:
            self.conectar()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def ejecutar_uno(self, query, params=()):
        if self.conn is None:
            self.conectar()
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def cerrar(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None


# instancia global (IMPORTANTE para todo el sistema)
db = DB()