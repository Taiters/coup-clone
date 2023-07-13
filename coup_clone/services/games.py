import random
import string
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from coup_clone.models import Game, db


def generate_game_id(length: int=6) -> str:
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def all() -> Sequence[Game]:
    return db.session.scalars(select(Game)).all()


def get(id: str) -> Optional[Game]:
    return db.session.get(Game, id)


def create() -> Game:
    try:
        game = Game(id=generate_game_id())
        db.session.add(game)
        db.session.commit()
        return game
    except IntegrityError:
        db.session.rollback()

        # We should really find an ID before hitting the recursion depth here
        # ...Not expecting many games to exist at once... sadly :(
        return create()
