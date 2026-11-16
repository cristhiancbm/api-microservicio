from pydantic import BaseModel, Field, HttpUrl, field_validator


# Lo que el cliente envía
class EnlaceCreate(BaseModel):
    url_enlace: HttpUrl = Field(
        ..., description="URL de la página a procesar", example="https://example.com"
    )
    @field_validator("url_enlace")
    @classmethod
    def validar_https(cls, value: HttpUrl) -> str:
        """Verifica que el protocolo sea estrictamente https"""
        if value.scheme != "https":
            raise ValueError(
                "La URL debe ser segura y utilizar el protocolo 'https://'"
            )
        return str(value)

# Lo que responde el endpoint (y puedes usar para la DB)
class EnlaceResponse(BaseModel):
    id: int
    url_enlace: str
    md_contenido: str

    class Config:
        from_attributes = True