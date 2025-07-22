import os
import psycopg2
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        print("¡Conexión a la base de datos exitosa!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None