from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coup_clone.database import Base


class Game(Base):
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    players: Mapped[List["Player"]] = relationship()


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    session_id: Mapped[str] = mapped_column(String(36))

    def __str__(self):
        return f"User: {self.name!r}"
