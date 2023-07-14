def test_game_setup_flow(app):
    client_a = app.test_client()
    client_b = app.test_client()

    games_response = client_a.get('/games')
    assert games_response.json['games'] == []

    created_game_response = client_a.post('/games')

    created_game_id = created_game_response.json['game_id']
    client_a.post('/games/'+created_game_id+'/players', json={
        'player_name': 'CLIENT A'
    })

    assert_players_in_game(client_a, created_game_id, {'CLIENT A'})

    client_b.post('/games/'+created_game_id+'/players', json={
        'player_name': 'CLIENT B'
    })
    assert_players_in_game(client_a, created_game_id, {'CLIENT A', 'CLIENT B'})

    client_b.delete('/games/' + created_game_id + '/players')
    assert_players_in_game(client_a, created_game_id, {'CLIENT A'})

    response = client_a.post('/games/'+created_game_id+'/players', json={
        'player_name': 'NEW CLIENT'
    })
    assert response.status_code == 409
    assert_players_in_game(client_a, created_game_id, {'CLIENT A'})

    client_a.delete('/games/' + created_game_id + '/players')
    assert_players_in_game(client_a, created_game_id, set())


def assert_players_in_game(client, game_id, players):
    game_response = client.get('/games/' + game_id)
    assert game_response.json['game_id'] == game_id
    assert len(game_response.json['players']) == len(players)
    assert {p['name'] for p in game_response.json['players']} == players