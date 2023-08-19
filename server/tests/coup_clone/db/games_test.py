import pytest
from aiosqlite import Cursor

from coup_clone.db.games import GameRow, GamesTable, GameState
from coup_clone.db.players import PlayerRow, PlayersTable


@pytest.mark.asyncio
async def test_create_game(cursor: Cursor):
    game = await GamesTable.create(cursor, id="1234", deck="abcd")

    assert game.id == "1234"
    assert game.deck == "abcd"
    assert game.state == GameState.LOBBY


@pytest.mark.asyncio
async def test_get_game(cursor: Cursor, game: GameRow):
    returned_game = await GamesTable.get(cursor, game.id)

    assert returned_game.id == game.id
    assert returned_game.deck == game.deck
    assert returned_game.state == game.state


@pytest.mark.asyncio
async def test_update_game(cursor: Cursor, game: GameRow):
    assert game.state == GameState.LOBBY

    await GamesTable.update(cursor, game.id, state=GameState.RUNNING)
    updated_game = await GamesTable.get(cursor, game.id)

    assert updated_game.id == game.id
    assert updated_game.deck == game.deck
    assert updated_game.state == GameState.RUNNING


@pytest.mark.asyncio
async def test_delete_game(cursor: Cursor, game: GameRow):
    await GamesTable.delete(cursor, game.id)
    game = await GamesTable.get(cursor, game.id)

    assert game is None


@pytest.mark.asyncio
async def test_delete_game_clears_players(
    cursor: Cursor,
    player: PlayerRow,
    game: GameRow,
):
    await GamesTable.delete(cursor, game.id)
    player = await PlayersTable.get(cursor, player.id)

    assert player is None
