import pytest
from aiohttp.test_utils import TestServer
from socketio import AsyncClient

from app import app_factory


@pytest.mark.asyncio
async def test_e2e_game(db_connection, mocker):
    session_callback = mocker.MagicMock()
    test_client = AsyncClient()

    test_client.on("session", session_callback)

    app = await app_factory()
    server = TestServer(app)
    await server.start_server()

    await test_client.connect(f"http://localhost:{server.port}")
    await test_client.disconnect()
    await server.close()

    session_callback.assert_called_once()
