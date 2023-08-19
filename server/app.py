import socketio
from aiohttp import web

from coup_clone import db
from coup_clone.handler import Handler
from coup_clone.managers.game import GameManager
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.managers.session import SessionManager

sio = socketio.AsyncServer(cors_allowed_origins="*", cookie="coup_session")


async def app_factory():
    async with db.open() as conn:
        await db.init(conn)
        await conn.commit()


    notifications_manager = NotificationsManager(sio)
    session_manager = SessionManager(sio, notifications_manager)
    game_manager = GameManager(sio, notifications_manager)

    app = web.Application()
    sio.attach(app)
    sio.register_namespace(Handler(session_manager, game_manager, notifications_manager))
    return app


if __name__ == "__main__":
    web.run_app(app_factory())
