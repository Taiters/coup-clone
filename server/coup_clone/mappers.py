from coup_clone.db.events import EventRow
from coup_clone.db.games import GameRow
from coup_clone.db.players import Influence, PlayerRow
from coup_clone.session import ActiveSession


def map_session(session: ActiveSession) -> dict:
    return {"id": session.id, "playerID": session.session.player_id}


def map_player(player: PlayerRow) -> dict:
    return {
        "id": player.id,
        "name": player.name,
        "state": player.state,
        "coins": player.coins,
        "influence": [
            player.influence_a if player.revealed_influence_a else Influence.UNKNOWN,
            player.influence_b if player.revealed_influence_b else Influence.UNKNOWN,
        ],
        "host": player.host,
    }


def map_event(event: EventRow) -> dict:
    return {
        "id": event.id,
        "timestamp": event.time_created.timestamp(),
        "actor": event.actor_id,
        "action": event.event_type,
    }


def map_game(game: GameRow) -> dict:
    return {
        "id": game.id,
        "state": game.state,
        "playerTurnID": game.current_player_turn,
    }
