from coup_clone.db.games import GameRow
from coup_clone.db.players import Influence, PlayerRow
from coup_clone.session import ActiveSession


def map_session(session: ActiveSession) -> dict:
    return {"id": session.id, "playerID": session.session.player_id}


def map_player(player: PlayerRow, session: ActiveSession) -> dict:
    influence = (
        [
            player.influence_a,
            player.influence_b,
        ]
        if session.session.player_id == player.id
        else [
            player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
            player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        ]
    )
    return {
        "id": player.id,
        "name": player.name,
        "state": player.state,
        "coins": player.coins,
        "influence": influence,
        "host": player.host,
    }


def map_game(game: GameRow) -> dict:
    return {
        "id": game.id,
        "state": game.state,
    }
