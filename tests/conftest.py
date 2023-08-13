from asyncio import Future
from uuid import uuid4
from aiosqlite import Connection, Cursor
import pytest
import pytest_asyncio
from coup_clone import db
from coup_clone.db.games import GameRow, GamesTable
from coup_clone.db.players import PlayerRow, PlayersTable
from coup_clone.db.sessions import SessionsTable


@pytest_asyncio.fixture
async def db_connection(mocker):
    mocker.patch('coup_clone.db.DB_FILE', ':memory:')
    async with db.open() as conn:
        await db.init(conn)
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


@pytest_asyncio.fixture
async def game(games_table: GamesTable, cursor: Cursor):
    return await games_table.create(cursor, id=str(uuid4()), deck='abcd')


@pytest_asyncio.fixture
async def player(players_table: PlayersTable, game: GameRow, cursor: Cursor):
    return await players_table.create(cursor, game_id=game.id)


@pytest_asyncio.fixture
async def session(sessions_table: SessionsTable, player: PlayerRow, cursor: Cursor):
    return await sessions_table.create(cursor, id=str(uuid4()), player_id=player.id)


@pytest.fixture
def socket_server(mocker):
    server = mocker.MagicMock()
    server.disconnect = mocker.AsyncMock()
    return server


@pytest.fixture
def socket_session(socket_server):
    session = {}
    socket_server.session.return_value.__aenter__.return_value = session
    return session
