import pytest
from aiosqlite import Connection
from socketio import AsyncServer

from coup_clone.db.players import PlayerRow
from coup_clone.db.sessions import SessionRow
from coup_clone.managers.session import (
    ActiveSession,
    NoActiveSessionException,
    SessionManager,
)


@pytest.mark.parametrize(
    "auth",
    [
        (None),
        ({}),
        ({"session": None}),
        ({"session": "shhhh"}),
    ],
)
@pytest.mark.asyncio
async def test_setup_without_existing_session(
    auth: dict,
    session_manager: SessionManager,
    socket_server: AsyncServer,
    socket_session: dict,
    db_connection: Connection,
):
    assert socket_session == {}

    session = await session_manager.setup(db_connection, "abcd", auth)

    assert socket_session["session"] == session.session.id
    socket_server.session.assert_called_with("abcd")
    socket_server.enter_room.assert_called_with("abcd", session.session.id)


@pytest.mark.asyncio
async def test_setup_with_existing_session(
    session: SessionRow,
    session_manager: SessionManager,
    socket_server: AsyncServer,
    socket_session: dict,
    db_connection: Connection,
):
    active_session = await session_manager.setup(db_connection, "abcd", {"session": session.id})

    assert socket_session["session"] == session.id
    assert active_session.session.id == session.id
    socket_server.enter_room.assert_called_with("abcd", session.id)


@pytest.mark.asyncio
async def test_get_without_existing_session_on_socket(
    session_manager: SessionManager,
    socket_session: dict,
    socket_server: AsyncServer,
    db_connection: Connection,
):
    with pytest.raises(NoActiveSessionException, match="session is not present in socket connection"):
        await session_manager.get(db_connection, "1234")
    socket_server.disconnect.assert_called_with("1234")


@pytest.mark.asyncio
async def test_get_without_existing_session_in_table(
    session_manager: SessionManager,
    socket_session: dict,
    socket_server: AsyncServer,
    db_connection: Connection,
):
    socket_session["session"] = "abcd"
    with pytest.raises(NoActiveSessionException, match="session not found in database"):
        await session_manager.get(db_connection, "1234")
    socket_server.disconnect.assert_called_with("1234")


@pytest.mark.asyncio
async def test_notify(
    session_manager: SessionManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    active_session: ActiveSession,
    player: PlayerRow,
):
    await session_manager.notify(db_connection, active_session)

    socket_server.emit.assert_called_with(
        "session",
        {
            "session": active_session.id,
            "currentGame": player.game_id,
        },
        room=active_session.id,
    )
