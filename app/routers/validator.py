import os
import requests
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from groq import Groq

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
def procesar_enlace(
    datos: EnlaceCreate, response: Response, db: Session = Depends(get_db)
):
    url_str = str(datos.url_enlace)

    try:
        # Paso 0: Verificar si ya existe en caché para no consumir la API de Groq
        enlace_existente = db.query(Enlace).filter(Enlace.url_enlace == url_str).first()
        if enlace_existente:
            return enlace_existente

        # Paso 1: Descargar el contenido HTML de la URL proporcionada
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response_http = requests.get(url_str, headers=headers, timeout=20)

        if response_http.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"No se pudo acceder a la URL. Código HTTP: {response_http.status_code}",
            )

        html_content = response_http.text[:15000]  # Limitamos caracteres por seguridad

        # Paso 2: Obtener automáticamente los modelos habilitados en tu cuenta/token
        lista_modelos_api = client.models.list().data

        # Filtramos modelos que NO son de generación de texto (audio, guard, orpheus/TTS)
        palabras_excluidas = ("whisper", "guard", "orpheus", "safeguard")
        modelos_disponibles = [
            m.id
            for m in lista_modelos_api
            if not any(palabra in m.id.lower() for palabra in palabras_excluidas)
        ]

        # (Opcional) Ponemos tu modelo principal primero si está en la lista para intentar con él antes que los demás
        if "qwen/qwen3.8-27b" in modelos_disponibles:
            modelos_disponibles.remove("qwen/qwen3.8-27b")
            modelos_disponibles.insert(0, "qwen/qwen3.8-27b")

        markdown_generado = None
        ultimo_error = None

        # Probamos automáticamente cada modelo disponible hasta que uno funcione
        for modelo_actual in modelos_disponibles:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Eres un asistente experto en convertir el DOM HTML de páginas web a un formato Markdown limpio, estructurado y legible.",
                        },
                        {
                            "role": "user",
                            "content": f"Por favor, convierte el siguiente contenido HTML/DOM de la URL '{url_str}' en un documento Markdown estructurado:\n\n{html_content}",
                        },
                    ],
                    model=modelo_actual,
                )

                markdown_generado = chat_completion.choices[0].message.content
                break  # Si funcionó, salimos del bucle

            except Exception as e:
                ultimo_error = e
                # Si falla por cuota (429), incompatibilidad o cualquier error del modelo, pasa al siguiente
                continue

        # Si probó todos los modelos de tu cuenta y ninguno pudo responder
        if not markdown_generado:
            raise HTTPException(
                status_code=429,
                detail=f"Ningún modelo disponible en tu cuenta pudo completar la petición. Último error: {str(ultimo_error)}",
            )

        # Paso 3: Almacenar en la base de datos MySQL usando SQLAlchemy
        nuevo_registro = Enlace(url_enlace=url_str, md_contenido=markdown_generado)
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)

        # Paso 4: Retornar la respuesta estructurada indicando que fue creado (201)
        response.status_code = status.HTTP_201_CREATED
        return nuevo_registro

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
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