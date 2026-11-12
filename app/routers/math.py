from fastapi import APIRouter, Depends
from app.schemas.math import SumRequest, SumResponse
from app.core.security import verificar_token
router = APIRouter(tags=["Math"])


@router.post("/sum", response_model=SumResponse, dependencies=[Depends
(verificar_token)])
def sumar_flotantes(payload: SumRequest):
    total = round(payload.num1 + payload.num2, 4)
    return SumResponse(resultado=total) 