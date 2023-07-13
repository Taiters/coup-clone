from coup_clone.services import games

def test_can_create_and_return_game(app):
    with app.app_context():
        game = games.create()
        returned_game = games.get(game.id)

    assert returned_game.id == game.id