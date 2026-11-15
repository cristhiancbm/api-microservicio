import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from groq import Groq
from typing import List

from app.database.config import get_db
from app.core.security import verificar_token
from app.schemas.enlace import EnlaceCreate, EnlaceResponse
from app.models.enlace import (
    Enlace,
)

load_dotenv()
router = APIRouter(tags=["Procesamiento de Enlaces"])

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@router.post(
    "/procesar-enlace",
    response_model=EnlaceResponse,
    dependencies=[Depends(verificar_token)],
)
def procesar_enlace(datos: EnlaceCreate, db: Session = Depends(get_db)):
    try:
        # Paso 1: Descargar el contenido HTML de la URL proporcionada
        # response_http = requests.get(datos.url_enlace, timeout=10)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response_http = requests.get(datos.url_enlace, headers=headers, timeout=20)

        if response_http.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"No se pudo acceder a la URL. Código HTTP: {response_http.status_code}",
            )

        html_content = response_http.text[
            :15000
        ]  # Limitamos caracteres por seguridad de tokens

        # Paso 2: Enviar el contenido al LLM (Groq) pidiendo formato Markdown
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en convertir el DOM HTML de páginas web a un formato Markdown limpio, estructurado y legible.",
                },
                {
                    "role": "user",
                    "content": f"Por favor, convierte el siguiente contenido HTML/DOM de la URL '{datos.url_enlace}' en un documento Markdown estructurado:\n\n{html_content}",
                },
            ],
            model="qwen/qwen3.8-27b",  # O el modelo Groq que estés utilizando
        )

        markdown_generado = chat_completion.choices[0].message.content

        # Paso 3: Almacenar en la base de datos MySQL usando SQLAlchemy
        nuevo_registro = Enlace(
            url_enlace=datos.url_enlace, md_contenido=markdown_generado
        )
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)

        # Paso 4: Retornar la respuesta estructurada
        return nuevo_registro

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/enlaces",
    response_model=List[EnlaceResponse],
    summary="Listar todos los enlaces y markdowns registrados",
    dependencies=[Depends(verificar_token)],
)
def listar_enlaces(db: Session = Depends(get_db)):
    """
    Retorna una lista con todas las URLs procesadas y sus respectivos markdowns almacenados en la base de datos.
    """
    try:
        enlaces = db.query(Enlace).all()
        return enlaces
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los enlaces: {str(e)}",
        )