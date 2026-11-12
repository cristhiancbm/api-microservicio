import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Carga las variables definidas en el archivo .env
load_dotenv()

# Lee las credenciales
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construye la URL de conexión para MySQL (requiere pymysql)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. Crea el motor de la base de datos
engine = create_engine(DATABASE_URL)

# 2. Crea la fábrica de sesiones (Sesiones para las transacciones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Clase Base de la cual heredarán todos tus modelos ORM (tablas)
class Base(DeclarativeBase):
    pass


# 4. Dependencia (Dependency Injection) para FastAPI
# Esta función abre una sesión con la base de datos por cada petición y la cierra al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()