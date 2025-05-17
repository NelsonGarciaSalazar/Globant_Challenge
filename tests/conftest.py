import pytest
from main import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infra.db.models import Base
from tests.mocks.blob_client import MockAzureBlobClient

# Override de la conexión
@pytest.fixture(scope="session", autouse=True)
def setup_mock_db():
    # SQLite en memoria
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)

    # Reemplazar sesión global temporalmente
    import infra.db.connection as db_conn
    db_conn.engine = engine
    db_conn.session_local = session_local

    yield  # aquí se ejecutan los tests

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(monkeypatch):
    # Monkeypatch del BlobClient
    monkeypatch.setattr("infra.storage.azure_blob.AzureBlobClient", MockAzureBlobClient)

    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
