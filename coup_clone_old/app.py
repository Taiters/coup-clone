from flask import Flask


def create_app(config_object: str = "coup_clone.config.ProdConfig") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    from coup_clone.models import db
    from coup_clone.socket import socketio

    db.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        db.create_all()

    from coup_clone.blueprints.games import games_bp

    app.register_blueprint(games_bp)

    return app
