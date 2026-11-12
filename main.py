from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.runner import crear_base_de_datos_si_no_existe, ejecutar_migraciones

from app.routers import health, math

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

# Endpoint GET raíz
@app.get("/")
def ruta_raiz():
    return {
        "estado": "exitoso",
        "mensaje": "Servidor activo y respondiendo correctamente."
    }