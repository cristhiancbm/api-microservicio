import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def crear_base_de_datos_si_no_existe():
    # 1. URL temporal SIN el nombre de la BD para conectarnos al servidor y crearla
    url_base = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    try:
        engine_temp = create_engine(url_base)
        with engine_temp.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            )
        print(f"Base de datos '{DB_NAME}' verificada/creada exitosamente.")
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")