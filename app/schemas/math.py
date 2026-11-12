from pydantic import BaseModel, Field


class SumRequest(BaseModel):
    num1: float = Field(..., description="Primer número flotante", example=3.0)
    num2: float = Field(..., description="Segundo número flotante", example=5.2)


class SumResponse(BaseModel):
    resultado: float = Field(..., example=8.2)