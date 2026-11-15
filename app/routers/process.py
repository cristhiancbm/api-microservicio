from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.persona import PersonaCreate, PersonaResponse
from app.database.config import get_db
from app.core.security import verificar_token
from app.models.persona import PersonaDB  # Asegúrate de tener tu modelo creado
from app.schemas.persona import (
    PersonaCreate,
    PersonaResponse,
)

router = APIRouter(prefix="/process", tags=["Procesos"])


@router.post("/", summary="Registrar información de personal", dependencies=[Depends(verificar_token)])
def procesar_persona(datos: PersonaCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el correo electrónico ya existe en la base de datos
    persona_existente = (
        db.query(PersonaDB).filter(PersonaDB.email == datos.email).first()
    )
    if persona_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado.",
        )

    # 2. Crear la instancia del modelo de base de datos con los datos validados
    nueva_persona = PersonaDB(
        nombre=datos.nombre,
        telefono=datos.telefono,
        celular=datos.celular,
        email=datos.email,
        genero=datos.genero,
    )

    # 3. Guardar en la base de datos
    try:
        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar en la base de datos: {str(e)}",
        )

    # 4. Retornar respuesta exitosa
    return {
        "mensaje": "Datos procesados y guardados exitosamente",
        "id": nueva_persona.id,
        "datos": datos,
    }
@router.get(
    "/",
    response_model=List[PersonaResponse],
    summary="Listar todas las personas registradas",
    dependencies=[Depends(verificar_token)],
)
def listar_personas(db: Session = Depends(get_db)):
    """
    Obtiene una lista con todos los registros de personas almacenados en la base de datos.
    Requiere autenticación Bearer Token.
    """
    try:
        # Consulta todos los registros de la tabla PersonaDB
        personas = db.query(PersonaDB).all()
        return personas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los registros: {str(e)}",
        )