import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_session(monkeypatch):
    mock_result = [
        MagicMock(_mapping={
            "id": 1,
            "department": "Sales",
            "hired": 25,
        }),
        MagicMock(_mapping={
            "id": 2,
            "department": "IT",
            "hired": 22,
        }),
    ]

    mock_session = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_session.close.return_value = None

    mock_session_local = MagicMock(return_value=mock_session)
    monkeypatch.setattr("api.routes.SessionLocal", mock_session_local)

    return mock_session

def test_hiring_above_average(client, mock_session):
    response = client.get("/report/hiring-above-average")
    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, list)
    assert data[0]["department"] == "Sales"
    assert data[0]["hired"] == 25
    assert any(dep["department"] == "IT" for dep in data)
