import socketio
from aiohttp import web

from coup_clone import db
from coup_clone.db.games import GameState, GamesTable
from coup_clone.handler import EventHandler


sio = socketio.AsyncServer(cors_allowed_origins='*', cookie='coup_session')

async def app_factory():
    async with db.open() as con:
        await db.init(con)
    
    async with db.open() as con:
        games = GamesTable()
        async with await con.cursor() as cursor:
            game = await games.get(cursor, 'jbznvg')
            print(game)
            await games.update(cursor, '1234', state=GameState.LOBBY)
            g2 = await games.get(cursor, '1234')
            print(g2)
        await con.commit()

    app = web.Application()
    sio.attach(app)
    sio.register_namespace(EventHandler())
    return app


if __name__ == '__main__':
    web.run_app(app_factory())
