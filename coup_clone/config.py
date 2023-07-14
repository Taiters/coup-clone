class Config:
    SECRET_KEY = "<TEST:OH NO PLEASE DONT SCRAPE ME>"
    TESTING = False


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
