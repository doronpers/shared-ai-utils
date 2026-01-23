"""WebSocket utilities for FastAPI."""

import json
import logging
from typing import Any, Callable, Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept a WebSocket connection.

        Args:
            websocket: WebSocket connection
            connection_id: Unique connection identifier
        """
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.debug(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str) -> None:
        """Disconnect a WebSocket connection.

        Args:
            connection_id: Connection identifier
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.debug(f"WebSocket disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific connection.

        Args:
            connection_id: Connection identifier
            message: Message dictionary to send

        Returns:
            True if sent successfully, False otherwise
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Connection not found: {connection_id}")
            return False

        websocket = self.active_connections[connection_id]
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
                return True
            else:
                self.disconnect(connection_id)
                return False
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            self.disconnect(connection_id)
            return False

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[list[str]] = None) -> int:
        """Broadcast a message to all connected clients.

        Args:
            message: Message dictionary to broadcast
            exclude: Optional list of connection IDs to exclude

        Returns:
            Number of connections that received the message
        """
        exclude = exclude or []
        sent_count = 0
        disconnected = []

        for connection_id, websocket in self.active_connections.items():
            if connection_id in exclude:
                continue

            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                    sent_count += 1
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)

        return sent_count

    def get_connection_count(self) -> int:
        """Get the number of active connections.

        Returns:
            Number of active connections
        """
        return len(self.active_connections)


async def websocket_endpoint(
    websocket: WebSocket,
    connection_id: str,
    manager: WebSocketManager,
    message_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> None:
    """Generic WebSocket endpoint handler.

    Args:
        websocket: WebSocket connection
        connection_id: Unique connection identifier
        manager: WebSocket manager instance
        message_handler: Optional function to handle incoming messages
    """
    await manager.connect(websocket, connection_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            # Handle message if handler provided
            if message_handler:
                try:
                    response = message_handler(message)
                    await websocket.send_json(response)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await websocket.send_json({"error": str(e)})
            else:
                # Echo message
                await websocket.send_json({"echo": message})

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.debug(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)
        raise
