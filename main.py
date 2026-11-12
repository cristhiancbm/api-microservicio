from fastapi import FastAPI

# Instancia principal de la aplicación
app = FastAPI(
    title="Mi API REST",
    description="API microservicio",
    version="1.0.0"
)

# Endpoint GET raíz
@app.get("/")
def ruta_raiz():
    return {
        "estado": "exitoso",
        "mensaje": "Servidor activo y respondiendo correctamente."
    }