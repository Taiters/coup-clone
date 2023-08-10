from aiohttp import web
import socketio

from coup_clone import database
from coup_clone.player import create_player
from coup_clone.game import create_game
from coup_clone.event import create_event, EventType

sio = socketio.AsyncServer()

async def app_factory():
    async with database.open_db() as db:
        await database.create_tables(db)
        game = await create_game(db)
        player = await create_player(db, game.id, '123456')
        event = await create_event(db, game.id, player.id, EventType.FOREIGN_AID, coins=2)
        print(game)
        print(player)
        print(event)
    app = web.Application()
    sio.attach(app)
    return app
    

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    print("message ", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    web.run_app(app_factory())