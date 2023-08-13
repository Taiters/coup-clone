from aiosqlite import Connection
import pytest
from coup_clone.handler import Handler

from coup_clone.managers.game import GameManager
from coup_clone.managers.session import ActiveSession, SessionManager


@pytest.fixture
def session_manager(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def game_manager(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def handler(session_manager, game_manager):
    return Handler(
        session_manager,
        game_manager,
    )


@pytest.mark.asyncio
async def test_on_connect(
    mocker,
    session_manager: SessionManager, 
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch('coup_clone.handler.db.open', return_value=conn)
    session_manager.setup.return_value = active_session

    await handler.on_connect('1234', {}, {})

    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_create_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager, 
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch('coup_clone.handler.db.open', return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == '1234' else None

    await handler.on_create_game('1234')

    game_manager.create.assert_called_with(conn.__aenter__.return_value, active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_join_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager, 
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch('coup_clone.handler.db.open', return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == '1234' else None

    await handler.on_join_game('1234', '5678')

    game_manager.join.assert_called_with(conn.__aenter__.return_value, '5678', active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_leave_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager, 
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch('coup_clone.handler.db.open', return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == '1234' else None

    await handler.on_leave_game('1234')

    game_manager.leave.assert_called_with(conn.__aenter__.return_value, active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_initialize_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager, 
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch('coup_clone.handler.db.open', return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == '1234' else None

    await handler.on_initialize_game('1234')

    game_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)
