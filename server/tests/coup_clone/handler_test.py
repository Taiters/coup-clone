import pytest
from socketio import AsyncServer
from socketio.exceptions import ConnectionRefusedError

from coup_clone.handler import Handler
from coup_clone.managers.game import (
    GameManager,
    GameNotFoundException,
    PlayerAlreadyInGameException,
)
from coup_clone.managers.session import ActiveSession, SessionManager


@pytest.fixture
def session_manager(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def game_manager(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def handler(socket_server, session_manager, game_manager):
    h = Handler(
        session_manager,
        game_manager,
    )
    h.server = socket_server
    return h


@pytest.mark.asyncio
async def test_on_connect_without_game_id(
    mocker,
    session_manager: SessionManager,
    game_manager: GameManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.setup.return_value = active_session

    await handler.on_connect("1234", {}, {})

    game_manager.join.assert_not_called()
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_connect_with_game_id(
    mocker,
    session_manager: SessionManager,
    game_manager: GameManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.setup.return_value = active_session

    await handler.on_connect("1234", {}, {"game": "abcd"})

    game_manager.join.assert_called_with(conn.__aenter__.return_value, "abcd", active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.parametrize(
    "error",
    [
        (PlayerAlreadyInGameException()),
        (GameNotFoundException()),
    ],
)
@pytest.mark.asyncio
async def test_on_connect_with_invalid_game_id_refuses_connection(
    error,
    mocker,
    session_manager: SessionManager,
    game_manager: GameManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.setup.return_value = active_session

    game_manager.join.side_effect = error

    with pytest.raises(ConnectionRefusedError):
        await handler.on_connect("1234", {}, {"game": "abcd"})


@pytest.mark.asyncio
async def test_on_create_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == "1234" else None

    await handler.on_create_game("1234")

    game_manager.create.assert_called_with(conn.__aenter__.return_value, active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.asyncio
async def test_on_create_game_disconnects_if_already_in_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    handler: Handler,
):
    game_manager.create.side_effect = PlayerAlreadyInGameException()

    with pytest.raises(PlayerAlreadyInGameException):
        await handler.on_create_game("1234")

    socket_server.disconnect.assert_called_with("1234", namespace="/")


@pytest.mark.asyncio
async def test_on_join_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == "1234" else None

    await handler.on_join_game("1234", "5678")

    game_manager.join.assert_called_with(conn.__aenter__.return_value, "5678", active_session)
    session_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)


@pytest.mark.parametrize(
    "error",
    [
        (PlayerAlreadyInGameException()),
        (GameNotFoundException()),
    ],
)
@pytest.mark.asyncio
async def test_on_join_game_disconnects_on_error(
    error,
    game_manager: GameManager,
    socket_server: AsyncServer,
    handler: Handler,
):
    game_manager.join.side_effect = error

    with pytest.raises(type(error)):
        await handler.on_join_game("1234", "5678")

    socket_server.disconnect.assert_called_with("1234", namespace="/")


@pytest.mark.asyncio
async def test_on_leave_game(
    mocker,
    game_manager: GameManager,
    session_manager: SessionManager,
    active_session: ActiveSession,
    handler: Handler,
):
    conn = mocker.MagicMock()
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == "1234" else None

    await handler.on_leave_game("1234")

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
    mocker.patch("coup_clone.handler.db.open", return_value=conn)
    session_manager.get.side_effect = lambda _, sid: active_session if sid == "1234" else None

    await handler.on_initialize_game("1234")

    game_manager.notify.assert_called_with(conn.__aenter__.return_value, active_session)
