from flask import Blueprint, abort
from flask.typing import ResponseReturnValue

from coup_clone.services import games

games_bp = Blueprint("games", __name__, url_prefix="/games")


@games_bp.post("/games/")
def create_game() -> ResponseReturnValue:
    game = games.create()
    return {
        "game_id": game.id,
    }


@games_bp.get("/games")
def get_games() -> ResponseReturnValue:
    return {
        "games": [g.id for g in games.all()],
    }


@games_bp.get("/game/<string:game_id>")
def game(game_id: str) -> ResponseReturnValue:
    game = games.get(game_id)
    if game is None:
        abort(404)

    return {
        "game_id": game.id,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "session_id": p.session_id,
            }
            for p in game.players
        ],
    }
