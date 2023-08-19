import random
from abc import ABC
from datetime import datetime, timedelta
from typing import Generic, Optional

from aiosqlite import Connection

from coup_clone.db.games import GameRow, GamesTable, TurnAction, TurnState
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable
from coup_clone.db.table import TID, T


class Model(ABC, Generic[T, TID]):
    def __init__(self, conn: Connection, row: T):
        self.conn = conn
        self.row = row

    @property
    def id(self) -> TID:
        return self.row.id


class Game(Model[GameRow, str]):
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

    async def get_next_player_turn(self) -> "Player":
        players = await self.get_players()
        if self.row.player_turn_id is None:
            return players[0]
        else:
            current_index = [p.id for p in players].index(self.row.player_turn_id)
            return players[(current_index + 1) % len(players)]


class Player(Model[PlayerRow, int]):
    @property
    def game_id(self) -> str:
        return self.row.game_id

    @property
    def influence_a(self) -> Influence:
        return self.row.influence_a

    @property
    def influence_b(self) -> Influence:
        return self.row.influence_a

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

    async def get_game(self) -> Game:
        async with self.conn.cursor() as cursor:
            game = await GamesTable.get(cursor, self.row.game_id)
        return Game(self.conn, game)


class Session(Model[SessionRow, str]):
    @property
    def player_id(self) -> Optional[int]:
        return self.row.player_id

    async def get_player(self) -> Optional[Player]:
        if self.player_id is None:
            return None

        async with self.conn.cursor() as cursor:
            player = await PlayersTable.get(cursor, self.player_id)
        return Player(self.conn, player)

    async def set_player(self, player_id: int) -> None:
        async with self.conn.cursor() as cursor:
            await SessionsTable.update(cursor, self.id, player_id=player_id)
        self.row.player_id = player_id

    async def clear_current_player(self) -> None:
        if self.player_id is None:
            return
        async with self.conn.cursor() as cursor:
            await PlayersTable.delete(
                cursor,
                self.player_id,
            )
        self.row.player_id = None
