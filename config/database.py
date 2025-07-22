import psycopg2
import os
from flask import g # 'g' es un objeto especial de Flask para almacenar datos durante una petición

def get_db():
    # Si no hay conexión en el contexto 'g' actual, la crea
    if 'db' not in g:
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            g.db = conn
        except psycopg2.OperationalError as e:
            print(f"Error al conectar con la base de datos: {e}")
            g.db = None # Asegúrate de que g.db sea None si falla
    return g.db

def close_db(e=None):
    # Cierra la conexión si existe al final de la petición
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app_db(app):
    # Le dice a Flask que llame a 'close_db' al limpiar después de una respuesta
    app.teardown_appcontext(close_db)
