import random
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Generic, Optional

from aiosqlite import Connection
from typing_extensions import Self

from coup_clone.db.games import GameRow, GamesTable, TurnAction, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable
from coup_clone.db.table import TID, T, Table


class Model(ABC, Generic[T, TID]):
    TABLE: type[Table[T, TID]]

    def __init__(self, conn: Connection, row: T):
        self.conn = conn
        self.row = row

    @property
    def id(self) -> TID:
        return self.row.id

    @classmethod
    async def create(cls, conn: Connection, **kwargs: Any) -> Self:
        async with conn.cursor() as cursor:
            row = await cls.TABLE.create(cursor, **kwargs)
            return cls(conn, row)

    @classmethod
    async def get(cls, conn: Connection, id: TID) -> Optional[Self]:
        async with conn.cursor() as cursor:
            row = await cls.TABLE.get(cursor, id)
            if row is not None:
                return cls(conn, row)
            return None

    async def update(self, **kwargs: Any) -> None:
        async with self.conn.cursor() as cursor:
            await self.TABLE.update(cursor, self.id, **kwargs)
            self.row = await self.TABLE.get(cursor, self.id)

    async def delete(self) -> None:
        async with self.conn.cursor() as cursor:
            await self.TABLE.delete(cursor, self.id)


class Game(Model[GameRow, str]):
    TABLE = GamesTable

    async def get_current_player(self) -> Optional["Player"]:
        if self.row.player_turn_id is None:
            return None
        return await Player.get(self.conn, self.row.player_turn_id)

    async def get_target_player(self) -> Optional["Player"]:
        if self.row.target_id is None:
            return None
        return await Player.get(self.conn, self.row.target_id)

    async def get_blocking_player(self) -> Optional["Player"]:
        if self.row.blocked_by_id is None:
            return None
        return await Player.get(self.conn, self.row.blocked_by_id)

    async def take_from_deck(self, n: int = 2) -> list[Influence]:
        deck = list(self.row.deck)
        popped = [Influence(int(deck.pop())) for i in range(n)]
        self.row.deck = "".join(deck)
        async with self.conn.cursor() as cursor:
            await GamesTable.update(cursor, self.id, deck=self.row.deck)
        return popped

    async def return_to_deck(self, influence: list[Influence]) -> None:
        deck = list(self.row.deck) + [i.value for i in influence]
        random.shuffle(deck)
        self.row.deck = "".join(str(c) for c in deck)
        async with self.conn.cursor() as cursor:
            await GamesTable.update(cursor, self.id, deck=self.row.deck)

    async def reset_turn_state(self, player_id: int) -> None:
        async with self.conn.cursor() as cursor:
            await GamesTable.update(
                cursor,
                self.id,
                player_turn_id=player_id,
                turn_state=TurnState.START,
                turn_action=None,
                target_id=None,
                challenged_by_id=None,
                blocked_by_id=None,
                block_challenged_by_id=None,
                turn_state_modified=datetime.utcnow(),
                turn_state_deadline=None,
            )
            await PlayersTable.reset_accepts_action(cursor, self.id)
            self.row = await GamesTable.get(cursor, self.id)

    async def set_action_deadline(self, action: TurnAction, seconds_from_now: int = 10) -> None:
        async with self.conn.cursor() as cursor:
            await GamesTable.update(
                cursor,
                self.id,
                turn_state_modified=datetime.utcnow(),
                turn_state_deadline=datetime.utcnow() + timedelta(seconds=seconds_from_now),
                turn_action=action,
                turn_state=TurnState.ATTEMPTED,
            )
            self.row = await GamesTable.get(cursor, self.id)

    async def get_players(self) -> list["Player"]:
        async with self.conn.cursor() as cursor:
            players = await PlayersTable.query(cursor, game_id=self.id, order_by=["id"])
        return [Player(self.conn, p) for p in players]

    async def get_next_player_turn(self) -> Optional["Player"]:
        players = [p for p in await self.get_players()]
        if self.row.player_turn_id is None:
            return players[0]
        else:
            current_index = [p.id for p in players].index(self.row.player_turn_id)
            player_sequence = players[current_index + 1 :] + players[: current_index + 1]
            return next(player for player in player_sequence if not player.is_out)

    async def all_players_accepted(self) -> bool:
        players = await self.get_players()
        return all(p.row.accepts_action for p in players if p.id != self.row.player_turn_id and not p.is_out)


class Player(Model[PlayerRow, int]):
    TABLE = PlayersTable

    @property
    def game_id(self) -> str:
        return self.row.game_id

    @property
    def influence_a(self) -> Influence:
        return self.row.influence_a

    @property
    def influence_b(self) -> Influence:
        return self.row.influence_b

    @property
    def is_out(self) -> bool:
        return self.row.revealed_influence_a and self.row.revealed_influence_b

    async def increment_coins(self, amount: int = 1) -> None:
        self.row.coins += amount
        async with self.conn.cursor() as cursor:
            await PlayersTable.update(
                cursor,
                self.id,
                coins=self.row.coins,
            )

    async def decrement_coins(self, amount: int = 1) -> None:
        self.row.coins -= amount
        async with self.conn.cursor() as cursor:
            await PlayersTable.update(
                cursor,
                self.id,
                coins=self.row.coins,
            )

    async def get_session(self) -> Optional["Session"]:
        async with self.conn.cursor() as cursor:
            sessions = await SessionsTable.query(cursor, player_id=self.id)
        if not sessions:
            return None
        return Session(self.conn, sessions[0])

    async def get_game(self) -> Game:
        async with self.conn.cursor() as cursor:
            game = await GamesTable.get(cursor, self.row.game_id)
        return Game(self.conn, game)


class Session(Model[SessionRow, str]):
    TABLE = SessionsTable

    @property
    def player_id(self) -> Optional[int]:
        return self.row.player_id

    async def get_player(self) -> Optional[Player]:
        if self.player_id is None:
            return None

        async with self.conn.cursor() as cursor:
            player = await PlayersTable.get(cursor, self.player_id)
        if player is None:
            return None
        return Player(self.conn, player)

    async def get_playerX(self) -> Player:
        player = await self.get_player()
        if player is None:
            raise Exception("OH no no player")
        return player

    async def set_player(self, player_id: int) -> None:
        async with self.conn.cursor() as cursor:
            await SessionsTable.update(cursor, self.id, player_id=player_id)
        self.row.player_id = player_id

    async def clear_current_player(self) -> None:
        if self.player_id is None:
            return
        await self.update(player_id=None)
        self.row.player_id = None
