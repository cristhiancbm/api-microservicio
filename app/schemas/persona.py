from pydantic import BaseModel, Field


class PersonaCreate(BaseModel):
    nombre: str = Field(
        ..., description="Nombre completo de la persona", example="Ana Pérez"
    )
    telefono: str = Field(None, description="Teléfono fijo opcional", example="2234567")
    celular: str = Field(
        ..., description="Número de celular obligatorio", example="76543210"
    )
    email: str = Field(
        ..., description="Correo electrónico único", example="ana@gmail.com"
    )
    genero: str = Field(None, description="Género", example="Femenino")