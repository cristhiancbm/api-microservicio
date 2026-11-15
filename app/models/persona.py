from sqlalchemy import Column, Integer, String
from app.database.config import Base


class PersonaDB(Base):
    __tablename__ = "personas"  # Debe coincidir exactamente con el nombre de la tabla en tu archivo .sql

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    genero = Column(String(20), nullable=True)
