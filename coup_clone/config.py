class Config:
    SECRET_KEY = "<TEST:OH NO PLEASE DONT SCRAPE ME>"
    TESTING = False


class ProdConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
