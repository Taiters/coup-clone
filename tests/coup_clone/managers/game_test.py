from aiosqlite import Connection, Cursor
import pytest
from socketio import AsyncServer
from coup_clone.db.games import GameRow, GameState, GamesTable
from coup_clone.db.players import PlayersTable
from coup_clone.db.sessions import SessionsTable
from coup_clone.managers.game import GameManager, GameNotFoundException, PlayerAlreadyInGameException
from coup_clone.managers.session import ActiveSession


@pytest.mark.asyncio
async def test_create(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
    games_table: GamesTable,
):
    session = await sessions_table.create(cursor, id='1234')
    active_session = ActiveSession(
        'sid',
        session,
        sessions_table,
        players_table,
    )

    (game_id, player) = await game_manager.create(db_connection, active_session)

    created_game = await games_table.get(cursor, game_id)
    created_player = await players_table.get(cursor, player.id)
    current_player = await active_session.current_player(cursor)

    assert created_game.state == GameState.LOBBY
    assert created_player.game_id == created_game.id
    assert active_session.session.player_id == created_player.id
    assert current_player.id == created_player.id
    socket_server.enter_room.assert_called_with('sid', created_game.id)


@pytest.mark.asyncio
async def test_create_when_already_in_a_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    active_session: ActiveSession,
):
    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.create(db_connection, active_session)
    socket_server.disconnect.assert_called_with(active_session.sid)
    

@pytest.mark.asyncio
async def test_join(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
    game: GameRow,
):
    session = await sessions_table.create(cursor, id='1234')
    active_session = ActiveSession(
        'sid',
        session,
        sessions_table,
        players_table,
    )

    (game_id, player) = await game_manager.join(db_connection, game.id, active_session)

    created_player = await players_table.get(cursor, player.id)
    current_player = await active_session.current_player(cursor)

    assert game_id == game.id
    assert created_player.game_id == game.id
    assert active_session.session.player_id == created_player.id
    assert current_player.id == created_player.id
    socket_server.enter_room.assert_called_with('sid', game.id)


@pytest.mark.asyncio
async def test_join_when_already_in_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    games_table: GamesTable,
    active_session: ActiveSession,
):
    new_game = await games_table.create(cursor, deck='abcd')

    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.join(db_connection, new_game.id, active_session)
    socket_server.disconnect.assert_called_with(active_session.sid)


@pytest.mark.asyncio
async def test_join_when_game_not_exists(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: GamesTable,
    players_table: PlayersTable,
):
    session = await sessions_table.create(cursor, id='1234')
    active_session = ActiveSession(
        'sid',
        session,
        sessions_table,
        players_table,
    )

    with pytest.raises(GameNotFoundException):
        await game_manager.join(db_connection, 'does not exist', active_session)
    socket_server.disconnect.assert_called_with(active_session.sid)


@pytest.mark.asyncio
async def test_leave(
    game_manager: GameManager,
    socket_server: AsyncServer,
    active_session: ActiveSession,
    db_connection: Connection,
    cursor: Cursor,
    game: GameRow,
):
    current_player = await active_session.current_player(cursor)
    assert current_player.game_id is not None

    await game_manager.leave(db_connection, active_session)

    current_player = await active_session.current_player(cursor)

    assert current_player is None
    assert active_session.session.player_id is None
    socket_server.leave_room.assert_called_with(active_session.sid, game.id)
