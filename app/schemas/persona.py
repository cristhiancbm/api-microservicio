from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PersonaCreate(BaseModel):
    nombre: str = Field(
        ..., description="Nombre completo de la persona", example="Ana Pérez"
    )
    telefono: Optional[str] = Field(None, description="Teléfono fijo opcional", example="2234567")
    celular: str = Field(
        ..., description="Número de celular obligatorio", example="76543210"
    )
    email: str = Field(
        ..., description="Correo electrónico único", example="ana@gmail.com"
    )
    genero: Optional[str] = Field(None, description="Género", example="Femenino")


class PersonaResponse(BaseModel):
    id: int
    nombre: str
    telefono: str | None = None
    celular: str | None = None
    email: str | None = None
    genero: str | None = None

    class Config:
        from_attributes = True