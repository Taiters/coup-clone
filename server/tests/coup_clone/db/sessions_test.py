from sqlite3 import IntegrityError

import pytest
from aiosqlite import Cursor

from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable


@pytest.mark.asyncio
async def test_create_session(cursor: Cursor, sessions_table: SessionsTable):
    session = await sessions_table.create(cursor, id="1234")

    assert session.id == "1234"
    assert session.player_id is None


@pytest.mark.asyncio
async def test_create_session_fails_with_missing_player(cursor: Cursor, sessions_table: SessionsTable):
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await sessions_table.create(cursor, id="1234", player_id=5678)


@pytest.mark.asyncio
async def test_create_session_with_player(cursor: Cursor, sessions_table: SessionsTable, player: PlayerRow):
    session = await sessions_table.create(cursor, id="1234", player_id=player.id)

    assert session.id == "1234"
    assert session.player_id == player.id


@pytest.mark.asyncio
async def test_delete_player_reflets_in_session(
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
    session: SessionRow,
    player: PlayerRow,
):
    assert session.player_id == player.id

    await players_table.delete(cursor, player.id)
    session = await sessions_table.get(cursor, session.id)

    assert session.id == session.id
    assert session.player_id is None


@pytest.mark.asyncio
async def test_update_session_fails_with_missing_player(
    cursor: Cursor, session: SessionRow, sessions_table: SessionsTable
):
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await sessions_table.update(cursor, session.id, player_id=12345)


@pytest.mark.asyncio
async def test_delete_session(cursor: Cursor, session: SessionRow, sessions_table: SessionsTable):
    await sessions_table.delete(cursor, session.id)
    session = await sessions_table.get(cursor, session.id)

    assert session is None
