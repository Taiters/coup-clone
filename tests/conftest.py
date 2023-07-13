import pytest
from coup_clone.app import create_app


@pytest.fixture(scope='session', autouse=True)
def app():
    app = create_app('coup_clone.config.TestConfig')

    yield app