from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
import json

from app.database.config import get_db
from app.models.mensaje import MensajeDB
from app.core.security import verificar_token_ws

router = APIRouter(tags=["Chat WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))

    async def send_to_user(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: str = None,
    db: Session = Depends(get_db),
):
    # Validación estricta del Token Bearer usando la lógica modularizada en security.py
    if not verificar_token_ws(token):
        await websocket.accept()
        await websocket.send_text(
            json.dumps({"tipo": "error", "mensaje": "Autenticación fallida: Token inválido o ausente"})
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(client_id, websocket)
    await manager.broadcast({"tipo": "sistema", "mensaje": f"El usuario '{client_id}' se ha conectado."})

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                destinatario = payload.get("destinatario", "todos")
                contenido = payload.get("contenido", "")

                nuevo_mensaje = MensajeDB(
                    remitente=client_id,
                    destinatario=destinatario,
                    contenido=contenido,
                )
                db.add(nuevo_mensaje)
                db.commit()

                mensaje_salida = {
                    "remitente": client_id,
                    "destinatario": destinatario,
                    "contenido": contenido,
                }

                if destinatario == "todos":
                    await manager.broadcast(mensaje_salida)
                else:
                    await manager.send_to_user(destinatario, mensaje_salida)
                    await manager.send_to_user(client_id, mensaje_salida)

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"tipo": "error", "mensaje": "Formato JSON inválido"}, websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast({"tipo": "sistema", "mensaje": f"El usuario '{client_id}' se ha desconectado."})