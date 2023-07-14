import random
import string
from typing import Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from coup_clone.models import Game, Player, db
from coup_clone.services import session


class PlayerAlreadyInGameException(Exception):
    pass


def generate_game_id(length: int = 6) -> str:
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def all() -> Sequence[Game]:
    return db.session.scalars(select(Game)).all()


def get(id: str) -> Optional[Game]:
    return db.session.get(Game, id)


def join(game_id: str, player_name: str) -> Player:
    player = Player(game_id=game_id, name=player_name, session_id=session.get_current_session_id())
    try:
        db.session.add(player)
        db.session.commit()
        return player
    except IntegrityError:
        db.session.rollback()
        raise PlayerAlreadyInGameException()


def leave(game_id: str) -> None:
    delete_statement = (
        delete(Player.__table__)
        .where(Player.session_id == session.get_current_session_id())
        .where(Player.game_id == game_id)
    )
    db.session.execute(delete_statement)
    db.session.commit()


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
