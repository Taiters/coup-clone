import random
import string

from flask import request

from flask_socketio import SocketIO, emit, send, join_room
from coup_clone.models import db, Game, Player, PlayerState

socketio = SocketIO(cors_allowed_origins='*')


DECK = "aaammmcccdddppp"


def _generate_game_id(length: int = 6) -> str:
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


@socketio.on("create")
def create_game():
    game_id = _generate_game_id()
    game = Game(id=game_id, deck=''.join(random.sample(DECK, k=len(DECK))))
    player = Player(game_id=game_id, session_id=request.sid)
    db.session.add(game)
    db.session.add(player)
    db.session.commit()
    join_room(game.id)
    emit("welcome", {
        "game": {
            "id": game.id,
            "state": game.state,
        },
        "players": [{
            "id": player.id,
            "state": player.state,
        }],
        "events": [],
        "currentPlayer": {
            "id": player.id,
            "state": player.state,
        }
    })


@socketio.on("join")
def join_game(data):
    game_id = data["game_id"]
    player = Player(game_id=game_id, session_id=request.sid)
    db.session.add(player)
    db.session.commit()
    game = db.session.get(Game, game_id)
    players = db.session.execute(
        db.select(Player)
            .filter_by(
                game_id=game_id,
            )
        ).scalars()

    join_room(game_id)
    emit("welcome", {
        "game": {
            "id": game.id,
            "state": game.state,
        },
        "players": [{
            "id": p.id,
            "state": p.state,
            "name": p.name,
        } for p in players],
        "events": [],
        "currentPlayer": {
            "id": player.id,
            "state": player.state,
        }
    })
    emit(
        "players_updated", 
        {
            "players": [{
                "id": player.id,
                "state": player.state,
                "name": player.name,
            } for player in players]
        },
        to=player.game_id
    )


@socketio.on("set_name")
def set_name(data):
    game_id = data["game_id"]
    name = data["name"]
    player = db.session.execute(
        db.select(Player)
            .filter_by(
                game_id=game_id,
                session_id=request.sid
            )
        ).scalar_one()

    player.name = name
    player.state = PlayerState.JOINED
    db.session.commit()

    players = db.session.execute(
        db.select(Player)
            .filter_by(
                game_id=game_id,
            )
        ).scalars()

    emit(
        "players_updated", 
        {
            "players": [{
                "id": player.id,
                "state": player.state,
                "name": player.name,
            } for player in players]
        },
        to=player.game_id
    )
