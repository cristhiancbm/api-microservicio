from fastapi import APIRouter, status, Depends
from app.core.security import verificar_token
router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK, dependencies=[Depends(verificar_token)])
def health_check():
    return {"status": "ok", "message": "Endpoint HEALTH"}