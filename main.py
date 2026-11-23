from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.runner import crear_base_de_datos_si_no_existe, ejecutar_migraciones
from app.routers import health, math, process, validator
from app.routers import health, math, process, validator, chat


from scalar_fastapi import get_scalar_api_reference

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_base_de_datos_si_no_existe()
    ejecutar_migraciones()
    yield


# Instancia principal de la aplicación
app = FastAPI(
    title="Mi API REST",
    description="API microservicio",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(math.router)
app.include_router(process.router)
app.include_router(validator.router)
app.include_router(chat.router)
# Endpoint GET raíz
@app.get("/")
def ruta_raiz():
    return {
        "estado": "exitoso",
        "mensaje": "Servidor activo y respondiendo correctamente."
    }
    # Endpoint para servir la documentación de Scalar
@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )