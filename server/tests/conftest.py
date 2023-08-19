from uuid import uuid4

import pytest
import pytest_asyncio
from aiosqlite import Connection, Cursor
from socketio import AsyncServer

from coup_clone import db
from coup_clone.db.games import GameRow, GamesTable
from coup_clone.db.players import Influence, PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionsTable
from coup_clone.managers.game import DECK, GameManager
from coup_clone.managers.notifications import NotificationsManager
from coup_clone.managers.session import ActiveSession, SessionManager


@pytest_asyncio.fixture
async def db_connection(mocker):
    mocker.patch("coup_clone.db.DB_FILE", ":memory:")
    async with db.open() as conn:
        await db.init(conn)
        open_mock = mocker.MagicMock()
        open_mock.__aenter__.return_value = conn
        mocker.patch("coup_clone.handler.db.open", return_value=open_mock)
        yield conn


@pytest_asyncio.fixture
async def cursor(db_connection: Connection):
    async with db_connection.cursor() as cursor:
        yield cursor


@pytest_asyncio.fixture
async def game(cursor: Cursor):
    return await GamesTable.create(cursor, id=str(uuid4()), deck="".join(str(c.value) for c in DECK))


@pytest_asyncio.fixture
async def player(game: GameRow, cursor: Cursor):
    return await PlayersTable.create(
        cursor, game_id=game.id, influence_a=Influence.CAPTAIN, influence_b=Influence.AMBASSADOR
    )


@pytest_asyncio.fixture
async def session(player: PlayerRow, cursor: Cursor):
    return await SessionsTable.create(cursor, id=str(uuid4()), player_id=player.id)


@pytest.fixture
def socket_server(mocker):
    server = mocker.MagicMock()
    server.disconnect = mocker.AsyncMock()
    server.emit = mocker.AsyncMock()
    return server


@pytest.fixture
def socket_session(socket_server):
    session = {}
    socket_server.session.return_value.__aenter__.return_value = session
    return session


@pytest.fixture
def active_session(socket_session, session):
    socket_session["session"] = session.id
    return ActiveSession(
        sid="1234",
        session=session,
    )


@pytest.fixture
def notifications_manager(
    socket_server: AsyncServer,
):
    return NotificationsManager(socket_server)


@pytest.fixture
def session_manager(
    socket_server: AsyncServer,
    notifications_manager: NotificationsManager,
):
    return SessionManager(socket_server, notifications_manager)


@pytest.fixture
def game_manager(
    socket_server: AsyncServer,
    notifications_manager: NotificationsManager,
):
    return GameManager(socket_server, notifications_manager)
