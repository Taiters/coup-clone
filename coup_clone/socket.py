from flask_socketio import SocketIO, send, join_room

socketio = SocketIO(cors_allowed_origins='*')


@socketio.on("message")
def handle_message(data):
    game_id = data["game_id"]
    name = data["name"]
    msg = data["msg"]
    send(name + " wrote: " + msg, to=game_id)


@socketio.on("join")
def handle_join(data):
    name = data["name"]
    game_id = data["game_id"]
    join_room(game_id)
    send(name + " joined " + game_id, to=game_id)
