import asyncio
from abc import ABC, abstractmethod
from http.cookies import SimpleCookie
from typing import Dict, Union, Callable, Coroutine, List, Any
from uuid import UUID

import injector
import socketio
from fastapi.encoders import jsonable_encoder
from injector import singleton, inject
from pydantic import BaseModel
from socketio import AsyncRedisManager

from auth.models import User
from auth.security import extract_user_from_token, decode_jwt_refresh_token
from chat.models import PrivateChat
from common.injection import injector
from config import cfg
from pubsub.store import WebSocketsStore

OnConnectCallback = Union[Callable[[str, User], Any], Coroutine]


class WsRouter(ABC):
    """Interface that should be implemented by every class that desires to
    define Socket.IO event handlers."""

    @abstractmethod
    def add_ws_routes(self, sio: socketio.AsyncServer):
        pass


class SioSession(BaseModel):
    """Socket.IO sid session object."""
    user: User
    private_chats: List[PrivateChat]


async def get_sio_session(sid: str) -> SioSession:
    """Return Socket.IO session object linked to specified sid."""
    return await injector.get(WebSockets).sio.get_session(sid)


async def save_sio_session(sid: str, session: SioSession) -> None:
    """Save Socket.IO session object, linking it to specified sid."""
    await injector.get(WebSockets).sio.save_session(sid, session)


@singleton
class WebSockets(WsRouter):
    @inject
    def __init__(
            self,
            store: WebSocketsStore):
        self._sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            client_manager=AsyncRedisManager(cfg.pubsub_uri),
            allow_upgrades=True)
        self._store = store
        self._on_connect_listeners: List[OnConnectCallback] = []
        self.include_ws_router(self)

    def include_socketio(self, app, path: str = "/"):
        """Mount Socket.IO on a FastAPI app at specified path."""
        socketio_asgi_app = socketio.ASGIApp(self._sio, app)
        app.mount(path, socketio_asgi_app)

    async def send(self, event: str, payload: Any, to: Union[str, UUID]) \
            -> None:
        """
        Send a message via websocket to specified room or sid.

        :param event: Socket.IO message event
        :param payload: Socket.IO message payload
        :param to: room id or sid
        """
        await self._sio.emit(event,
                             jsonable_encoder(payload),
                             room=str(to))

    def subscribe_to_on_connect(self, callback: OnConnectCallback):
        """Link a callback to the 'on_connect' Socket.IO event."""
        self._on_connect_listeners.append(callback)

    def unsubscribe_from_on_connect(self, callback: OnConnectCallback):
        """Unlink a callback from the 'on_connect' Socket.IO event."""
        self._on_connect_listeners.remove(callback)

    @property
    def sio(self) -> socketio.AsyncServer:
        """Return the Socket.IO instance."""
        return self._sio

    @property
    def store(self) -> WebSocketsStore:
        """Return the WebSocketsStore instance."""
        return self._store

    def include_ws_router(self, router: WsRouter):
        router.add_ws_routes(self._sio)

    def add_ws_routes(self, sio: socketio.AsyncServer):
        sio.on("connect", self._on_connect)
        sio.on("disconnect", self._on_disconnect)
        sio.on("ping", self._on_ping)

    async def _notify_on_connect_listeners(self, sid: str, user: User):
        for listener in self._on_connect_listeners:
            await listener(sid, user) if asyncio.iscoroutinefunction(listener) \
                else listener(sid, user)

    async def _on_connect(self, sid: str, environ: Dict, auth: Dict):
        # WebSocket authentication method: check access token signature only and
        # verify refresh token signature and expiration
        token = auth and auth.get("token")
        if not token:
            return False
        try:
            user = extract_user_from_token(token, verify_exp=False)
            cookie = SimpleCookie()
            cookie.load(environ["HTTP_COOKIE"])
            decode_jwt_refresh_token(cookie["refresh_token"].value,
                                     verify_exp=True)
        except Exception as e:
            return False
        self._sio.enter_room(sid=sid, room=str(user.id))
        await self._store.renew_online_status(str(user.id))
        await self._notify_on_connect_listeners(sid, user)

    async def _on_ping(self, sid: str):
        if session := await get_sio_session(sid):
            await self._store.renew_online_status(session.user.id)

    async def _on_disconnect(self, sid: str):
        if session := await get_sio_session(sid):
            self._sio.leave_room(sid=sid, room=str(session.user.id))
