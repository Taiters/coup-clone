from __future__ import annotations

import enum
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Boolean, String, Integer, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

db = SQLAlchemy()


class GameState(enum.IntEnum):
    LOBBY = 0
    RUNNING = 1


class PlayerState(enum.IntEnum):
    JOINING = 0
    JOINED = 1


class EventType(enum.IntEnum):
    INCOME = 0
    FOREIGN_AID = 1
    EXCHANGE = 2
    TAX = 3
    STEAL = 4
    ASSASSINATE = 5
    COUP = 6
    BLOCK = 7
    CHALLENGE = 8
    GIVE = 9
    REVEAL = 10
    OUT = 11
    WIN = 12


class EventOutcome(enum.IntEnum):
    PENDING = 0
    SUCCESS = 1
    FAIL = 2


class Influence(enum.IntEnum):
    DUKE = 0
    AMBASSADOR = 1
    ASSASSIN = 2
    CONTESSA = 3
    CAPTAIN = 4


class Game(db.Model):  # type: ignore
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    state: Mapped[GameState] = mapped_column(Enum(GameState), default=GameState.LOBBY)
    players: Mapped[List["Player"]] = relationship()
    game_events: Mapped[List["GameEvent"]] = relationship()
    deck: Mapped[str] = mapped_column(String(15))


class Player(db.Model):  # type: ignore
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("game_id", "session_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[PlayerState] = mapped_column(Enum(PlayerState), default=PlayerState.JOINING)
    name: Mapped[str] = mapped_column(String(15), nullable=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    coins: Mapped[int] = mapped_column(Integer, default=3)
    session_id: Mapped[str] = mapped_column(String(36))
    influence_a: Mapped[Influence] = mapped_column(Enum(Influence), nullable=True)
    influence_b: Mapped[Influence] = mapped_column(Enum(Influence), nullable=True)
    revealed_influence_a: Mapped[bool] = mapped_column(Boolean, default=False)
    revealed_influence_b: Mapped[bool] = mapped_column(Boolean, default=False)


class GameEvent(db.Model): # type: ignore
    __tablename__ = "game_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    time_created: Mapped[DateTime]= mapped_column(DateTime(timezone=True), server_default=func.now())
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    parent: Mapped[int] = mapped_column(ForeignKey("game_events.id"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType))
    coins: Mapped[int] = mapped_column(Integer, nullable=True)
    revealed: Mapped[Influence] = mapped_column(Enum(Influence), nullable=True)
    outcome: Mapped[EventOutcome] = mapped_column(Enum(EventOutcome), default=EventOutcome.PENDING)
