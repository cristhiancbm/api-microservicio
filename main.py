from fastapi import FastAPI

from app.routers import health

# Instancia principal de la aplicación
app = FastAPI(
    title="Mi API REST",
    description="API microservicio",
    version="1.0.0"
)

app.include_router(health.router)

# Endpoint GET raíz
@app.get("/")
def ruta_raiz():
    return {
        "estado": "exitoso",
        "mensaje": "Servidor activo y respondiendo correctamente."
    }