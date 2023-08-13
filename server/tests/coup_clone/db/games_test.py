import pytest
from aiosqlite import Cursor

from coup_clone.db.games import GameRow, GamesTable, GameState
from coup_clone.db.players import PlayerRow, PlayersTable


@pytest.mark.asyncio
async def test_create_game(cursor: Cursor, games_table: GamesTable):
    game = await games_table.create(cursor, id="1234", deck="abcd")

    assert game.id == "1234"
    assert game.deck == "abcd"
    assert game.state == GameState.LOBBY


@pytest.mark.asyncio
async def test_get_game(cursor: Cursor, game: GameRow, games_table: GamesTable):
    returned_game = await games_table.get(cursor, game.id)

    assert returned_game.id == game.id
    assert returned_game.deck == game.deck
    assert returned_game.state == game.state


@pytest.mark.asyncio
async def test_update_game(cursor: Cursor, game: GameRow, games_table: GamesTable):
    assert game.state == GameState.LOBBY

    await games_table.update(cursor, game.id, state=GameState.RUNNING)
    updated_game = await games_table.get(cursor, game.id)

    assert updated_game.id == game.id
    assert updated_game.deck == game.deck
    assert updated_game.state == GameState.RUNNING


@pytest.mark.asyncio
async def test_delete_game(cursor: Cursor, game: GameRow, games_table: GamesTable):
    await games_table.delete(cursor, game.id)
    game = await games_table.get(cursor, game.id)

    assert game is None


@pytest.mark.asyncio
async def test_delete_game_clears_players(
    cursor: Cursor, player: PlayerRow, game: GameRow, players_table: PlayersTable, games_table: GamesTable
):
    await games_table.delete(cursor, game.id)
    player = await players_table.get(cursor, player.id)

    assert player is None
