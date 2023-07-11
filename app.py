import random
import string
from uuid import uuid4

from flask import Flask, g, jsonify, session
from sqlalchemy import select

from coup_clone.database import db_session
from coup_clone.models import Game, Player

app = Flask(__name__)

app.secret_key = b"<TEST:OH NO PLEASE DONT SCRAPE ME>"


def get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    return session["session_id"]


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/games")
def games():
    games = db_session.scalars(select(Game)).all()
    return jsonify(games=[g.id for g in games])


@app.route("/game/<string:game_id>")
def game(game_id: str):
    game = db_session.get(Game, game_id)
    return jsonify(
        game_id=game.id,
        players=[
            {
                "id": p.id,
                "name": p.name,
                "session_id": p.session_id,
            }
            for p in game.players
        ],
    )


@app.route("/game/<string:game_id>/join/<string:name>")
def join_game(game_id: str, name: str):
    game = db_session.get(Game, game_id)
    player = Player(name=name, game_id=game_id, session_id=get_session_id())
    db_session.add(player)
    db_session.commit()
    return jsonify(player_id=player.id, name=player.name, game_id=player.game_id, session_id=player.session_id)


@app.route("/game/create")
def create_game():
    game_id = "".join([random.choice(string.ascii_lowercase) for _ in range(6)])
    game = Game(id=game_id)
    db_session.add(game)
    db_session.commit()
    return jsonify(game_id=game.id)
