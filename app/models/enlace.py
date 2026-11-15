from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.database.config import (
    Base,
)


class Enlace(Base):
    __tablename__= "enlaces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url_enlace = Column(String(500), nullable=False)
    md_contenido = Column(LONGTEXT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())