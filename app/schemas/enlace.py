from pydantic import BaseModel, Field


# Lo que el cliente envía
class EnlaceCreate(BaseModel):
    url_enlace: str = Field(
        ..., description="URL de la página a procesar", example="https://example.com"
    )


# Lo que responde el endpoint (y puedes usar para la DB)
class EnlaceResponse(BaseModel):
    id: int
    url_enlace: str
    md_contenido: str

    class Config:
        from_attributes = True