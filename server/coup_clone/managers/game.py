import random
import string
from dataclasses import dataclass
from sqlite3 import IntegrityError
from typing import Tuple

from aiosqlite import Connection, Cursor
from socketio import AsyncServer

from coup_clone.db.events import EventsTable, EventType
from coup_clone.db.games import GamesTable, GameState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable, PlayerState
from coup_clone.managers.exceptions import (
    GameFullException,
    GameNotFoundException,
    NotEnoughPlayersException,
    NotPlayerTurnException,
    PlayerAlreadyInGameException,
    PlayerNotInGameException,
)
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.session import ActiveSession

DECK = [
    Influence.DUKE,
    Influence.DUKE,
    Influence.DUKE,
    Influence.CAPTAIN,
    Influence.CAPTAIN,
    Influence.CAPTAIN,
    Influence.ASSASSIN,
    Influence.ASSASSIN,
    Influence.ASSASSIN,
    Influence.CONTESSA,
    Influence.CONTESSA,
    Influence.CONTESSA,
    Influence.AMBASSADOR,
    Influence.AMBASSADOR,
    Influence.AMBASSADOR,
]


@dataclass
class GameAction:
    action_type: EventType


class GameManager:
    def __init__(
        self,
        socket_server: AsyncServer,
        notifications_manager: NotificationsManager,
        games_table: GamesTable,
        players_table: PlayersTable,
        events_table: EventsTable,
    ):
        self.socket_server = socket_server
        self.notifications_manager = notifications_manager
        self.games_table = games_table
        self.players_table = players_table
        self.events_table = events_table

    async def _take_from_deck(self, cursor: Cursor, game_id: str, n: int = 2) -> list[Influence]:
        game = await self.games_table.get(cursor, game_id)
        if game is None:
            raise GameNotFoundException()
        deck = list(game.deck)
        popped = [Influence(int(deck.pop())) for i in range(n)]
        await self.games_table.update(cursor, game.id, deck="".join(deck))
        return popped

    async def _return_to_deck(self, cursor: Cursor, game_id: str, influence: list[Influence]) -> None:
        game = await self.games_table.get(cursor, game_id)
        if game is None:
            raise GameNotFoundException()
        deck = list(game.deck) + [i.value for i in influence]
        random.shuffle(deck)
        await self.games_table.update(cursor, game.id, deck="".join(str(c) for c in deck))

    async def create(self, conn: Connection, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            game_id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
            game = await self.games_table.create(
                cursor, id=game_id, deck="".join(str(c.value) for c in random.sample(DECK, k=len(DECK)))
            )
            hand = await self._take_from_deck(cursor, game_id)
            player = await self.players_table.create(
                cursor, game_id=game.id, host=True, influence_a=hand[0], influence_b=hand[1]
            )
            await self.games_table.update(cursor, game.id, current_player_turn=player.id)
            await session.set_current_player(cursor, player.id)
            await conn.commit()
        self.socket_server.enter_room(session.sid, game.id)
        await self.notifications_manager.notify_session(conn, session)
        return (game.id, player)

    async def join(self, conn: Connection, game_id: str, session: ActiveSession) -> Tuple[str, PlayerRow]:
        async with conn.cursor() as cursor:
            current_player = await session.current_player(cursor)
            if current_player is not None:
                raise PlayerAlreadyInGameException("Already in game " + current_player.game_id)

            hand = await self._take_from_deck(cursor, game_id)
            try:
                player = await self.players_table.create(
                    cursor, game_id=game_id, influence_a=hand[0], influence_b=hand[1]
                )
            except IntegrityError as e:
                if str(e) == "Game full":
                    raise GameFullException()
            await session.set_current_player(cursor, player.id)
            await conn.commit()

        self.socket_server.enter_room(session.sid, game_id)
        await self.notifications_manager.broadcast_game_players(conn, game_id)
        await self.notifications_manager.notify_session(conn, session)
        return (game_id, player)

    async def leave(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is not None:
                await self._return_to_deck(cursor, player.game_id, [player.influence_a, player.influence_b])
                await session.clear_current_player(cursor)
                await conn.commit()
                self.socket_server.leave_room(session.sid, player.game_id)
                await self.notifications_manager.broadcast_game_players(conn, player.game_id)
        await self.notifications_manager.notify_session(conn, session)

    async def set_name(self, conn: Connection, session: ActiveSession, name: str) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            await self.players_table.update(cursor, player.id, name=name, state=PlayerState.READY)
            await conn.commit()
        await self.notifications_manager.broadcast_game_players(conn, player.game_id)

    async def start(self, conn: Connection, session: ActiveSession) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            player_count = await self.players_table.count(cursor, game_id=player.game_id, state=PlayerState.READY)
            if player_count < 2:
                raise NotEnoughPlayersException()
            await self.games_table.update(cursor, player.game_id, state=GameState.RUNNING)
            await conn.commit()
        await self.notifications_manager.broadcast_game(conn, player.game_id)

    async def take_action(self, conn: Connection, session: ActiveSession, action: GameAction) -> None:
        async with conn.cursor() as cursor:
            player = await session.current_player(cursor)
            if player is None:
                raise PlayerNotInGameException()
            game = await self.games_table.get(cursor, player.game_id)
            if game.current_player_turn != player.id:
                raise NotPlayerTurnException()
            await self.events_table.create(
                cursor, game_id=player.game_id, actor_id=player.id, event_type=action.action_type
            )
            await conn.commit()
        await self.notifications_manager.broadcast_game(conn, player.game_id)
        await self.notifications_manager.broadcast_game_events(conn, player.game_id)
