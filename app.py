import socketio
from aiohttp import web

from coup_clone import db
from coup_clone.db.events import EventsTable
from coup_clone.db.games import GamesTable
from coup_clone.db.players import PlayersTable
from coup_clone.db.sessions import SessionsTable
from coup_clone.handler import Handler
from coup_clone.managers.game import GameManager
from coup_clone.managers.session import SessionManager


sio = socketio.AsyncServer(cors_allowed_origins='*', cookie='coup_session')

async def app_factory():
    async with db.open() as con:
        await db.init(con)
    

    games_table = GamesTable()
    events_table = EventsTable()
    players_table = PlayersTable()
    sessions_table = SessionsTable()
    session_manager = SessionManager(
        sio,
        sessions_table,
        players_table
    )
    game_manager = GameManager(
        sio,
        games_table,
        players_table
    )
    

    app = web.Application()
    sio.attach(app)
    sio.register_namespace(Handler(session_manager, game_manager))
    return app


if __name__ == '__main__':
    web.run_app(app_factory())
