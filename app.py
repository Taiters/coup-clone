from aiohttp import web
import socketio

from coup_clone import database, games, players
from coup_clone.players import Influence, Player
from coup_clone.games import Game

sio = socketio.AsyncServer(cors_allowed_origins='*', cookie='coup_session')

async def app_factory():
    async with database.open_db() as db:
        await database.create_tables(db)
    app = web.Application()
    sio.attach(app)
    return app


def _player_json(player: Player) -> dict:
    return {
        'id': player.id,
        'name': player.name,
        'state': player.state,
        'coins': player.coins,
        'influence': [
            player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
            player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        ]
    }


def _game_json(game: Game) -> dict:
    return {
        'id': game.id,
        'state': game.state,
        'currentPlayerTurn': None,
    }


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.event
async def create_game(sid):
    async with database.open_db() as db:
        game = await games.create_game(db)
        player = await players.create_player(db, game.id, sid)
    return game.id


@sio.event
async def join_game(sid, game_id):
    async with database.open_db() as db:
        await players.create_player(db, game_id, sid)
        game_players = await players.get_players_in_game(db, game_id)
    await sio.emit('update_players', [_player_json(p) for p in game_players], room=game_id)
    return game_id


@sio.event
async def enter_game(sid, game_id):
    async with database.open_db() as db:
        game = await games.get_game(db, game_id)
        game_players = await players.get_players_in_game(db, game.id)
        game_events = []
    sio.enter_room(sid, game_id)
    return {
        'game': _game_json(game),
        'players': [_player_json(p) for p in game_players],
        'events': [],
        'currentPlayer': next((_player_json(p) for p in game_players if p.session_id == sid))
    }


@sio.event
async def set_name(sid, name):
    async with database.open_db() as db:
        player = await players.set_name(db, sid, name)
        game_players = await players.get_players_in_game(db, player.game_id)
    await sio.emit('update_players', [_player_json(p) for p in game_players], room=player.game_id)


if __name__ == '__main__':
    web.run_app(app_factory())