import pytest
from coup_clone import database
from coup_clone.handler import EventHandler


@pytest.mark.asyncio
async def test_handler_thing(mocker):
    mock_session = mocker.MagicMock()
    mock_session.__aenter__.return_value = {'session': 'current-session'}
    mocker.patch('coup_clone.database.DB_FILE', 1234)
    mocker.patch('coup_clone.handler.EventHandler.session', return_value=mock_session)

    async with database.open_db() as db:
        await database.create_tables(db)

    handler = EventHandler()
    await handler.on_connect('1234', None, {})