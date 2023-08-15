from uuid import uuid4

import pytest
import pytest_asyncio
from aiosqlite import Connection, Cursor
from socketio import AsyncServer

from coup_clone import db
from coup_clone.db.events import EventsTable
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


@pytest.fixture
def games_table():
    return GamesTable()


@pytest.fixture
def players_table():
    return PlayersTable()


@pytest.fixture
def sessions_table():
    return SessionsTable()


@pytest.fixture
def events_table():
    return EventsTable()


@pytest_asyncio.fixture
async def game(games_table: GamesTable, cursor: Cursor):
    return await games_table.create(cursor, id=str(uuid4()), deck="".join(str(c.value) for c in DECK))


@pytest_asyncio.fixture
async def player(players_table: PlayersTable, game: GameRow, cursor: Cursor):
    return await players_table.create(
        cursor, game_id=game.id, influence_a=Influence.CAPTAIN, influence_b=Influence.AMBASSADOR
    )


@pytest_asyncio.fixture
async def session(sessions_table: SessionsTable, player: PlayerRow, cursor: Cursor):
    return await sessions_table.create(cursor, id=str(uuid4()), player_id=player.id)


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
def active_session(socket_session, session, sessions_table, players_table):
    socket_session["session"] = session.id
    return ActiveSession(
        sid="1234",
        session=session,
        sessions_table=sessions_table,
        players_table=players_table,
    )


@pytest.fixture
def notifications_manager(
    socket_server: AsyncServer,
    games_table: GamesTable,
    players_table: PlayersTable,
    events_table: EventsTable,
):
    return NotificationsManager(socket_server, games_table, players_table, events_table)


@pytest.fixture
def session_manager(
    socket_server: AsyncServer,
    notifications_manager: NotificationsManager,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
):
    return SessionManager(socket_server, notifications_manager, sessions_table, players_table)


@pytest.fixture
def game_manager(
    socket_server: AsyncServer,
    notifications_manager: NotificationsManager,
    games_table: GamesTable,
    players_table: PlayersTable,
    events_table: EventsTable,
):
    return GameManager(socket_server, notifications_manager, games_table, players_table, events_table)
