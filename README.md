# Microservicio REST con FastAPI, MySQL y Cloudflare Tunnel

Este proyecto es un microservicio desarrollado en **FastAPI**, conectado a una base de datos **MySQL**, asegurado mediante autenticación por **Token Bearer (`APIKeyHeader`)** y expuesto a internet de forma segura mediante **Cloudflare Quick Tunnels**.

## Flujo de la API

![Flujo de la API](docs/diagramas/flujo-api.svg)

[Abrir diagrama interactivo](docs/diagramas/flujo-api.html)

## Rutas de la API

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/` | No | Comprobación simple: devuelve `estado: exitoso` y un mensaje de servidor activo. |
| `GET` | `/scalar` | No | Documentación alternativa con Scalar (`include_in_schema=False`). |
| `GET` | `/health` | Bearer | Health protegido; responde `{"status": "ok"}`. |
| `POST` | `/sum` | Bearer | Suma `num1` y `num2`, redondea a 4 decimales y devuelve `resultado`. |
| `POST` | `/process/` | Bearer | Registra una persona: valida email duplicado (400), guarda en MySQL y devuelve `id` y datos. |
| `GET` | `/process/` | Bearer | Lista todas las personas registradas. |
| `POST` | `/procesar-enlace` | Bearer | Descarga el HTML de una URL, lo convierte a Markdown con Groq, guarda en `enlaces` y responde 201; reutiliza la caché si ya existe. |
| `GET` | `/enlaces` | Bearer | Lista todos los enlaces y sus Markdown almacenados. |
| `WS` | `/ws/{client_id}` | Token en query (`token`) | Chat en tiempo real: guarda mensajes en `mensajes` y los envía al destinatario o a todos. |

> FastAPI también expone automáticamente `/docs`, `/redoc` y `/openapi.json`. Las rutas protegidas requieren el header `Authorization: Bearer <token>`.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados en tu sistema:

- **Python 3.10+**
- **MySql**
- **Git**

## 1. Instalación y Configuración del Entorno

1. **Clona el repositorio y entra al directorio del proyecto:**

   ```bash
   git clone https://github.com/cristhiancbm/api-microservicio.git
   cd api-microservicio
   ```

2. **Crea y activa un entorno virtual:**
   - **En Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **En Windows (PowerShell):**
     ```bash
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. **Instala las dependencias del proyecto:**
   ```bash
   pip install -r requirements.txt
   ```
   _(Asegúrate de incluir paquetes como `fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `pydantic`)._

## 2. Ejecutar el Backend (FastAPI)

Con el entorno virtual activado y la base de datos en marcha, levanta el servidor de desarrollo con Uvicorn:

```bash
uvicorn main:app --reload
```

- El servidor estará disponible localmente en: `http://localhost:8000`
- Documentación interactiva (Swagger UI): `http://localhost:8000/docs`

### Autenticación Bearer

Los endpoints protegidos requieren el envío de un token estático utilizando el esquema **Bearer** en el encabezado HTTP `Authorization`:

- **Header:** `Authorization`
- **Formato del Valor:** `Bearer clave_secreta_token`

_(En Swagger UI, haz clic en el botón **Authorize**, e introduce el token con el prefijo o formato configurado, por ejemplo, `123456` o `Bearer 123456` según tu esquema actual de validación)._

## 3. Exponer el Servicio con Cloudflare Tunnel (`cloudflared`)

Para hacer accesible la API desde internet mediante HTTPS sin abrir puertos en el router ni requerir un dominio propio, utilizamos un **Quick Tunnel** (Tunel temporal) de Cloudflare.

### Paso A: Instalar `cloudflared`

- **En Linux (64-bit):**

  ```bash
  curl -L --output cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod +x cloudflared
  sudo mv cloudflared /usr/local/bin/
  ```

- **En Windows (PowerShell como Administrador):**
  ```powershell
  winget install Cloudflare.cloudflared
  ```

Verifica la instalación ejecutando:

```bash
cloudflared --version
```

### Paso B: Iniciar el Túnel Rápido (Quick Tunnel)

Con tu servidor FastAPI corriendo en el puerto `8000`, abre **otra terminal** y ejecuta:

```bash
cloudflared tunnel --url http://localhost:8000
```

### Paso C: Probar la URL Pública

En las primeras líneas de salida de la terminal aparecerá un recuadro con tu URL pública temporal generada automáticamente, con el siguiente formato:

```text
https://<nombre-aleatorio>.trycloudflare.com
```

1. Copia esa URL y ábrela en tu navegador añadiendo **`/docs`** al final:
   ```text
   https://<nombre-aleatorio>.trycloudflare.com/docs
   ```
2. Haz clic en **Authorize**, introduce el token Bearer correspondiente y prueba tus endpoints desde cualquier red o dispositivo.

## Notas Adicionales

- **Túneles Temporales:** El comando `--url` genera un subdominio aleatorio cada vez que se reinicia el proceso. No requiere iniciar sesión ni poseer un dominio registrado en Cloudflare.
- **Terminales Simultáneas:** Recuerda mantener tanto `uvicorn` como `cloudflared` ejecutándose en paralelo mientras utilices el servicio de forma remota.
