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

def ejecutar_migraciones():
    # 2. IMPORTANTE: Importamos el engine AQUÍ ADENTRO. 
    from app.database.config import engine

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        result = connection.execute(text("SELECT version FROM schema_migrations"))
        migraciones_aplicadas = {row[0] for row in result}

        carpeta_migrations = "migrations"
        if not os.path.exists(carpeta_migrations):
            os.makedirs(carpeta_migrations)
            return

        archivos = sorted(os.listdir(carpeta_migrations))

        for archivo in archivos:
            if archivo.endswith(".sql") and archivo not in migraciones_aplicadas:
                ruta_archivo = os.path.join(carpeta_migrations, archivo)
                print(f"Aplicando migración: {archivo}...")

                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    sql_script = f.read()

                for sentencia in sql_script.split(";"):
                    if sentencia.strip():
                        connection.execute(text(sentencia))

                connection.execute(
                    text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                    {"version": archivo},
                )
                print(f"Migración {archivo} aplicada exitosamente.")

if __name__ == "__main__":
    crear_base_de_datos_si_no_existe()
    ejecutar_migraciones()