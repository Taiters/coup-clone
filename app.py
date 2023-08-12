import socketio
from aiohttp import web

from coup_clone import database
from coup_clone.handler import EventHandler


sio = socketio.AsyncServer(cors_allowed_origins='*', cookie='coup_session')

async def app_factory():
    async with database.open_db() as db:
        await database.create_tables(db)
    
    app = web.Application()
    sio.attach(app)
    sio.register_namespace(EventHandler())
    return app


if __name__ == '__main__':
    web.run_app(app_factory())
