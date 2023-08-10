from flask import Blueprint, abort, request
from flask.typing import ResponseReturnValue

from coup_clone.services import games

games_bp = Blueprint("games", __name__, url_prefix="/games")


@games_bp.post("")
def create_game() -> ResponseReturnValue:
    game = games.create()
    return {
        "game_id": game.id,
    }


@games_bp.get("")
def get_games() -> ResponseReturnValue:
    return {
        "games": [g.id for g in games.all()],
    }


@games_bp.get("/<string:game_id>")
def get_game(game_id: str) -> ResponseReturnValue:
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


@games_bp.post("/<string:game_id>/players")
def join_game(game_id: str) -> ResponseReturnValue:
    data = request.get_json()
    player_name = data.get("player_name", None)
    if player_name is None or type(player_name) != str:
        abort(400)

    try:
        player = games.join(game_id, player_name)
        return {
            "id": player.id,
            "game_id": player.game_id,
            "session_id": player.session_id,
        }
    except games.PlayerAlreadyInGameException:
        abort(409)


@games_bp.delete("/<string:game_id>/players")
def leave_game(game_id: str) -> ResponseReturnValue:
    games.leave(game_id)
    return {}
