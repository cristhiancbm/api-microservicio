import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

# Esto le indica a FastAPI que busque el token directamente en el Header "Authorization"
oauth2_scheme = APIKeyHeader(name="Authorization")

TOKEN_SECRETO_VALIDO = os.getenv("API_SECRET_TOKEN", "cristhian")


def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    # Limpiamos por si el usuario escribe "Bearer 123456" o solo "123456"
    token_limpio_recibido = token.replace("Bearer ", "").strip()

    if token_limpio_recibido != TOKEN_SECRETO_VALIDO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return token


def verificar_token_ws(token: str | None) -> bool:
    """Valida el token para WebSockets donde el token se pasa como parámetro de consulta o string."""
    token_limpio = (token or "").replace("Bearer ", "").strip()
    return token_limpio == TOKEN_SECRETO_VALIDO