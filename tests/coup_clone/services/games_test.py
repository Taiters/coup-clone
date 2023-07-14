import pytest
from coup_clone.services import games

def test_can_create_and_return_game(app):
    with app.app_context():
        game = games.create()
        returned_game = games.get(game.id)

        assert returned_game.id == game.id


def test_can_player_join_game(app, mocker):
    mocker.patch('coup_clone.services.session.get_current_session_id', return_value='<SESSION_ID>')
    with app.app_context():
        game = games.create()
        player = games.join(game_id=game.id, player_name="test")

        assert game.players == [player]


def test_can_player_leave_game(app, mocker):
    mocker.patch('coup_clone.services.session.get_current_session_id', return_value='<SESSION_ID>')
    with app.app_context():
        game = games.create()

        games.join(game_id=game.id, player_name="test")
        games.leave(game_id=game.id)

        assert game.players == []
    


def test_single_session_per_game(app, mocker):
    mocker.patch('coup_clone.services.session.get_current_session_id', return_value='<SESSION_ID>')
    with app.app_context():
        game = games.create()
        games.join(game_id=game.id, player_name="test")

        with pytest.raises(games.PlayerAlreadyInGameException):
            games.join(game_id=game.id, player_name="test")
    
