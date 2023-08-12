from functools import reduce
from socketio import AsyncNamespace
from aiosqlite import Connection
from typing import Optional

from coup_clone import database, events, games, players, sessions
from coup_clone.players import Influence, Player
from coup_clone.games import Game, GameState
from coup_clone.events import Event, EventType


def _player_json(player: Player) -> dict:
    return {
        'id': player.id,
        'name': player.name,
        'state': player.state,
        'coins': player.coins,
        'influence': [
            player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
            player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        ],
        'host': player.host,
    }


def _game_json(game: Game) -> dict:
    return {
        'id': game.id,
        'state': game.state,
        'currentPlayerTurn': None,
    }


def _event_json(event: Event, parent_to_children: dict[int, list[Event]]):
    event_json = {
        'id': event.id,
        'timestamp': int(event.time_created.timestamp()),
        'actor': event.actor_id,
        'target': event.target_id,
        'action': event.event_type,
        'coins': event.coins,
        'revealed': event.revealed,
        'success': event.success,
    }
    if event.id in parent_to_children:
        event_json['children'] = [_event_json(c, parent_to_children) for c in parent_to_children[event.id]]
    return event_json


def _add_to_map(map: dict[int, list[Event]], event: Event) -> dict[int, list[Event]]:
    if event.parent_id not in map:
        map[event.parent_id] = []
    map[event.parent_id].append(event)
    return map


def _events_json(events: list[Event]):
    parent_to_children = reduce(_add_to_map, events, {})
    return [_event_json(e, parent_to_children) for e in events if e.parent_id is None]


async def _get_valid_session(db: Connection, auth: Optional[dict[str, str]]) -> str:
    session_id = auth.get('sessionID', None) if auth is not None else None
    if session_id is not None:
        if await sessions.check_session(db, session_id):
            return session_id
    session_id = await sessions.create_session(db)
    await db.commit()
    return session_id


class EventHandler(AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        async with database.open_db() as db:
            session_id = await _get_valid_session(db, auth)
            player = await players.get_player_from_session(db, session_id)

        async with self.session(sid) as socket_session:
            socket_session['session'] = session_id

        await self.emit('session', {
            'sessionID': session_id,
            'currentGameID': player.game_id if player is not None else None
        }, room=sid)
        print('connect ', sid)


    def on_disconnect(self, sid):
        print('disconnect ', sid)


    async def on_create_game(self, sid):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                game_id = await games.create_game(db)
                player_id = await players.create_player(db, game_id, True)
                await sessions.set_player(db, socket_session['session'], player_id)
                e = await events.create_event(db, game_id, player_id, EventType.INCOME, coins=1)
                await events.create_event(db, game_id, player_id, EventType.BLOCK, target_id=player_id, parent_id=e)
                await db.commit()
        return game_id


    async def on_join_game(self, sid, game_id):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                player_id = await players.create_player(db, game_id)
                await sessions.set_player(db, socket_session['session'], player_id)
                await db.commit()
                game_players = await players.get_players_in_game(db, game_id)
        await self.emit('update_players', [_player_json(p) for p in game_players], room=game_id)
        return game_id


    async def on_enter_game(self, sid):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                player = await players.get_player_from_session(db, socket_session['session'])
                game = await games.get_game(db, player.game_id)
                game_players = await players.get_players_in_game(db, game.id)
                game_events = await events.get_events_for_game(db, game.id)
        self.enter_room(sid, game.id)
        return {
            'game': _game_json(game),
            'players': [_player_json(p) for p in game_players],
            'events': _events_json(game_events),
            'currentPlayer': next((_player_json(p) for p in game_players if p.id == player.id))
        }


    async def on_leave_game(self, sid):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                player = await players.get_player_from_session(db, socket_session['session'])
                await players.delete_player(db, player.id)
                players_remaining = await players.get_players_in_game(db, player.game_id)
                if not players_remaining:
                    await games.delete_game(db, player.game_id)
                await db.commit()
            await self.emit('update_players', [_player_json(p) for p in players_remaining], room=player.game_id, skip_sid=sid)
            await self.emit('session', {
                'sessionID': socket_session['session'],
                'currentGameID': None,
            }, room=sid)


    async def on_start_game(self, sid):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                player = await players.get_player_from_session(db, socket_session['session'])
                if not player.host:
                    raise Error("Only host can start")
                await games.set_state(db, player.game_id, games.GameState().RUNNING)
                game = await games.get_game(db, player.game_id)
                await db.commit()
        await self.emit('update_game', _game_json(game), room=game.id)
        

    async def on_set_name(self, sid, name):
        async with self.session(sid) as socket_session:
            async with database.open_db() as db:
                player = await players.get_player_from_session(db, socket_session['session'])
                await players.set_name(db, player.id, name)
                await db.commit()
                game_players = await players.get_players_in_game(db, player.game_id)
        await self.emit('update_players', [_player_json(p) for p in game_players], room=player.game_id)