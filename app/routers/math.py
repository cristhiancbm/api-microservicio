from fastapi import APIRouter
from app.schemas.math import SumRequest, SumResponse

router = APIRouter(tags=["Math"])


@router.post("/sum", response_model=SumResponse)
def sumar_flotantes(payload: SumRequest):
    total = round(payload.num1 + payload.num2, 4)
    return SumResponse(resultado=total) 