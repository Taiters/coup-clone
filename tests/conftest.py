import pytest
from coup_clone.app import create_app


@pytest.fixture
def app():
    app = create_app('coup_clone.config.TestConfig')

    yield app
