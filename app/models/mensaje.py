from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database.config import Base


class MensajeDB(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    remitente = Column(String(100), nullable=False, index=True)
    destinatario = Column(String(100), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp())