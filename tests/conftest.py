import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infra.db.models import Base
import infra.db.connection as db_conn
from main import create_app

@pytest.fixture(autouse=True)
def reset_database():
    from infra.db.models import Base
    from tests.conftest import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

db_conn.engine = engine
db_conn.SessionLocal = SessionLocal

Base.metadata.create_all(engine)

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("infra.db.connection.engine", engine)
    monkeypatch.setattr("infra.db.connection.SessionLocal", SessionLocal)
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
