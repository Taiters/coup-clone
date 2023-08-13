from aiosqlite import Connection
import pytest
from socketio import AsyncServer
from coup_clone.db.players import PlayersTable
from coup_clone.db.sessions import SessionRow, SessionsTable

from coup_clone.managers.session import SessionManager


@pytest.fixture
def session_manager(
    socket_server: AsyncServer,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
):
    return SessionManager(
        socket_server,
        sessions_table,
        players_table
    )


@pytest.mark.parametrize(
    'auth',
    [
        (None),
        ({}),
        ({'session': None}),
        ({'session': 'shhhh'}),
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

    session = await session_manager.setup(db_connection, 'abcd', auth)

    assert socket_session['session'] == session.session.id
    socket_server.session.assert_called_with('abcd')
    socket_server.enter_room.assert_called_with('abcd', session.session.id)


@pytest.mark.asyncio
async def test_setup_with_existing_session(
    session: SessionRow,
    session_manager: SessionManager,
    socket_server: AsyncServer,
    socket_session: dict,
    db_connection: Connection
):
    active_session = await session_manager.setup(db_connection, 'abcd', {'session': session.id})

    assert socket_session['session'] == session.id
    assert active_session.session.id == session.id
    socket_server.enter_room.assert_called_with('abcd', session.id)


@pytest.mark.asyncio
async def test_get_without_existing_session_on_socket(
    session_manager: SessionManager,
    socket_session: dict,
    db_connection: Connection,
):
    with pytest.raises(ValueError, match='session is not present in socket connection'):
        await session_manager.get(db_connection, '1234')


@pytest.mark.asyncio
async def test_get_without_existing_session_in_table(
    session_manager: SessionManager,
    socket_session: dict,
    db_connection: Connection,
):
    socket_session['session'] = 'abcd'
    with pytest.raises(ValueError, match='session not found in database'):
        await session_manager.get(db_connection, '1234')
