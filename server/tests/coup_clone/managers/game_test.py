from uuid import uuid4

import pytest
from aiosqlite import Connection, Cursor
from socketio import AsyncServer

from coup_clone.db.games import GameRow, GamesTable, GameState
from coup_clone.db.players import Influence, PlayersTable
from coup_clone.db.sessions import SessionsTable
from coup_clone.managers.exceptions import (
    GameFullException,
    GameNotFoundException,
    PlayerAlreadyInGameException,
)
from coup_clone.managers.game import DECK, GameManager
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
    session = await sessions_table.create(cursor, id="1234")
    active_session = ActiveSession(
        "sid",
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
    socket_server.enter_room.assert_called_with("sid", created_game.id)


@pytest.mark.asyncio
async def test_create_when_already_in_a_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    active_session: ActiveSession,
):
    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.create(db_connection, active_session)


@pytest.mark.asyncio
async def test_join(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
    games_table: GamesTable,
    game: GameRow,
):
    session = await sessions_table.create(cursor, id="1234")
    active_session = ActiveSession(
        "sid",
        session,
        sessions_table,
        players_table,
    )

    (game_id, player) = await game_manager.join(db_connection, game.id, active_session)

    created_player = await players_table.get(cursor, player.id)
    current_player = await active_session.current_player(cursor)
    joined_game = await games_table.get(cursor, game_id)

    assert game_id == game.id
    assert created_player.game_id == game.id
    assert created_player.influence_a == Influence(int(game.deck[-2]))
    assert created_player.influence_b == Influence(int(game.deck[-1]))
    assert joined_game.deck == game.deck[0:-2]
    assert active_session.session.player_id == created_player.id
    assert current_player.id == created_player.id
    socket_server.enter_room.assert_called_with("sid", game.id)


@pytest.mark.asyncio
async def test_join_when_already_in_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    games_table: GamesTable,
    active_session: ActiveSession,
):
    new_game = await games_table.create(cursor, deck="abcd")

    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.join(db_connection, new_game.id, active_session)


@pytest.mark.asyncio
async def test_join_limits_up_to_6_players(
    game_manager: GameManager,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
    games_table: GamesTable,
    active_session: ActiveSession,
):
    new_game = await games_table.create(cursor, id=str(uuid4()), deck="".join(str(c.value) for c in DECK))
    await db_connection.commit()
    session_rows = [await sessions_table.create(cursor, id=str(uuid4())) for _ in range(7)]
    sessions = [
        ActiveSession(
            str(uuid4()),
            r,
            sessions_table,
            players_table,
        )
        for r in session_rows
    ]

    for s in sessions[:6]:
        await game_manager.join(db_connection, new_game.id, s)

    with pytest.raises(GameFullException):
        await game_manager.join(db_connection, new_game.id, sessions[-1])

    players = await players_table.query(cursor, game_id=new_game.id)
    assert len(players) == 6

    await game_manager.leave(db_connection, sessions[1])
    await game_manager.join(db_connection, new_game.id, sessions[-1])

    players = await players_table.query(cursor, game_id=new_game.id)
    assert len(players) == 6


@pytest.mark.asyncio
async def test_join_when_game_not_exists(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    sessions_table: SessionsTable,
    players_table: PlayersTable,
):
    session = await sessions_table.create(cursor, id="1234")
    active_session = ActiveSession(
        "sid",
        session,
        sessions_table,
        players_table,
    )

    with pytest.raises(GameNotFoundException):
        await game_manager.join(db_connection, "does not exist", active_session)


@pytest.mark.asyncio
async def test_leave(
    game_manager: GameManager,
    games_table: GamesTable,
    socket_server: AsyncServer,
    active_session: ActiveSession,
    db_connection: Connection,
    cursor: Cursor,
    game: GameRow,
):
    current_player = await active_session.current_player(cursor)
    assert current_player.game_id is not None
    player_influence = [
        str(current_player.influence_a.value),
        str(current_player.influence_b.value),
    ]
    game_deck = list(game.deck)

    await game_manager.leave(db_connection, active_session)

    current_player = await active_session.current_player(cursor)
    game = await games_table.get(cursor, game.id)

    assert current_player is None
    assert active_session.session.player_id is None
    assert sorted(list(game.deck)) == sorted(game_deck + player_influence)
    socket_server.leave_room.assert_called_with(active_session.sid, game.id)
