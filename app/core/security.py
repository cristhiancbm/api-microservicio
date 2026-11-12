from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Esto le indica a FastAPI que busque el token directamente en el Header "Authorization"
oauth2_scheme = APIKeyHeader(name="Authorization")


def verificar_token(token: str = Depends(oauth2_scheme)):
    token_secreto_valido = "cristhian"

    # Limpiamos por si el usuario escribe "Bearer 123456" o solo "123456"
    token_limpio_recibido = token.replace("Bearer ", "").strip()

    if token_limpio_recibido != token_secreto_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return token

    