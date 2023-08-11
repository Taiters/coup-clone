from aiohttp import web
import socketio
from aiosqlite import Connection
from typing import Optional

from coup_clone import database, games, players, sessions
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


async def _get_valid_session(db: Connection, auth: Optional[dict[str, str]]) -> str:
    session_id = auth.get('sessionID', None) if auth is not None else None
    if session_id is not None:
        if await sessions.check_session(db, session_id):
            return session_id
    session_id = await sessions.create_session(db)
    await db.commit()
    return session_id


@sio.event
async def connect(sid, environ, auth):
    async with database.open_db() as db:
        session_id = await _get_valid_session(db, auth)
        player = await players.get_player_from_session(db, session_id)

    async with sio.session(sid) as socket_session:
        socket_session['session'] = session_id

    await sio.emit('session', {
        'sessionID': session_id,
        'currentGameID': player.game_id if player is not None else None
    })
    print('connect ', sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.event
async def create_game(sid):
    async with sio.session(sid) as socket_session:
        async with database.open_db() as db:
            game_id = await games.create_game(db)
            player_id = await players.create_player(db, game_id)
            await sessions.set_player(db, socket_session['session'], player_id)
            await db.commit()
    return game_id


@sio.event
async def join_game(sid, game_id):
    async with sio.session(sid) as socket_session:
        async with database.open_db() as db:
            player_id = await players.create_player(db, game_id)
            await sessions.set_player(db, socket_session['session'], player_id)
            await db.commit()
            game_players = await players.get_players_in_game(db, game_id)
    await sio.emit('update_players', [_player_json(p) for p in game_players], room=game_id)
    return game_id


@sio.event
async def enter_game(sid):
    async with sio.session(sid) as socket_session:
        async with database.open_db() as db:
            player = await players.get_player_from_session(db, socket_session['session'])
            game = await games.get_game(db, player.game_id)
            game_players = await players.get_players_in_game(db, game.id)
            game_events = []
    sio.enter_room(sid, game.id)
    return {
        'game': _game_json(game),
        'players': [_player_json(p) for p in game_players],
        'events': game_events,
        'currentPlayer': next((_player_json(p) for p in game_players if p.id == player.id))
    }


@sio.event
async def set_name(sid, name):
    async with sio.session(sid) as socket_session:
        async with database.open_db() as db:
            player = await players.get_player_from_session(db, socket_session['session'])
            await players.set_name(db, player.id, name)
            await db.commit()
            game_players = await players.get_players_in_game(db, player.game_id)
    await sio.emit('update_players', [_player_json(p) for p in game_players], room=player.game_id)


if __name__ == '__main__':
    web.run_app(app_factory())