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
from coup_clone.models import Session
from coup_clone.request import Request


@pytest.mark.asyncio
async def test_create(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
):
    session = await SessionsTable.create(cursor, id="1234")
    request = Request(
        sid="sid",
        session=Session()(cursor, session),
    )

    (game_id, player) = await game_manager.create(db_connection, request)

    created_game = await GamesTable.get(cursor, game_id)
    created_player = await PlayersTable.get(cursor, player.id)
    current_player = await request.session.get_player()

    assert created_game.state == GameState.LOBBY
    assert created_player.game_id == created_game.id
    assert request.session.player_id == created_player.id
    assert current_player.id == created_player.id
    socket_server.enter_room.assert_called_with("sid", created_game.id)


@pytest.mark.asyncio
async def test_create_when_already_in_a_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    current_request: Request,
):
    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.create(db_connection, current_request)


@pytest.mark.asyncio
async def test_join(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    game: GameRow,
):
    session = await SessionsTable.create(cursor, id="1234")
    request = Request(
        sid="sid",
        session=Session()(cursor, session),
    )

    (game_id, player) = await game_manager.join(db_connection, game.id, request)

    created_player = await PlayersTable.get(cursor, player.id)
    current_player = await request.session.get_player()
    joined_game = await GamesTable.get(cursor, game_id)

    assert game_id == game.id
    assert created_player.game_id == game.id
    assert created_player.influence_a == Influence(int(game.deck[-2]))
    assert created_player.influence_b == Influence(int(game.deck[-1]))
    assert joined_game.deck == game.deck[0:-2]
    assert request.session.player_id == created_player.id
    assert current_player.id == created_player.id
    socket_server.enter_room.assert_called_with("sid", game.id)


@pytest.mark.asyncio
async def test_join_when_already_in_game(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
    current_request: Request,
):
    new_game = await GamesTable.create(cursor, deck="abcd")

    with pytest.raises(PlayerAlreadyInGameException):
        await game_manager.join(db_connection, new_game.id, current_request)


@pytest.mark.asyncio
async def test_join_limits_up_to_6_players(
    game_manager: GameManager,
    db_connection: Connection,
    cursor: Cursor,
    current_request: Request,
):
    new_game = await GamesTable.create(cursor, id=str(uuid4()), deck="".join(str(c.value) for c in DECK))
    await db_connection.commit()
    session_rows = [await SessionsTable.create(cursor, id=str(uuid4())) for _ in range(7)]
    requests = [
        Request(
            sid=str(uuid4()),
            session=Session(cursor, r),
        )
        for r in session_rows
    ]

    for r in requests[:6]:
        await game_manager.join(db_connection, new_game.id, r)

    with pytest.raises(GameFullException):
        await game_manager.join(db_connection, new_game.id, requests[-1])

    players = await PlayersTable.query(cursor, game_id=new_game.id)
    assert len(players) == 6

    await game_manager.leave(db_connection, requests[1])
    await game_manager.join(db_connection, new_game.id, requests[-1])

    players = await PlayersTable.query(cursor, game_id=new_game.id)
    assert len(players) == 6


@pytest.mark.asyncio
async def test_join_when_game_not_exists(
    game_manager: GameManager,
    socket_server: AsyncServer,
    db_connection: Connection,
    cursor: Cursor,
):
    session = await SessionsTable.create(cursor, id="1234")
    request = Request(
        sid="sid",
        session=Session()(cursor, session),
    )

    with pytest.raises(GameNotFoundException):
        await game_manager.join(db_connection, "does not exist", request)


@pytest.mark.asyncio
async def test_leave(
    game_manager: GameManager,
    socket_server: AsyncServer,
    current_request: Request,
    db_connection: Connection,
    cursor: Cursor,
    game: GameRow,
):
    current_player = await current_request.session.get_player()
    assert current_player.game_id is not None
    player_influence = [
        str(current_player.influence_a.value),
        str(current_player.influence_b.value),
    ]
    game_deck = list(game.deck)

    await game_manager.leave(db_connection, current_request)

    current_player = await current_request.session.get_player()
    game = await GamesTable.get(cursor, game.id)

    assert current_player is None
    assert current_request.session.player_id is None
    assert sorted(list(game.deck)) == sorted(game_deck + player_influence)
    socket_server.leave_room.assert_called_with(current_request.sid, game.id)
