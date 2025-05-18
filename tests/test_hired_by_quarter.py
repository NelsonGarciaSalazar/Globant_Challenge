import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_session(monkeypatch):
    mock_result = [
        MagicMock(_mapping={
            "department": "Sales",
            "job": "Manager",
            "Q1": 1,
            "Q2": 2,
            "Q3": 0,
            "Q4": 0,
        }),
        MagicMock(_mapping={
            "department": "IT",
            "job": "Engineer",
            "Q1": 0,
            "Q2": 0,
            "Q3": 1,
            "Q4": 3,
        }),
    ]

    mock_session = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_session.close.return_value = None

    mock_session_local = MagicMock(return_value=mock_session)

    monkeypatch.setattr("api.routes.SessionLocal", mock_session_local)

    return mock_session

def test_hired_by_quarter_mock(client, mock_session):
    response = client.get("/report/hired-by-quarter")
    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, list)
    assert data[0]["department"] == "Sales"
    assert data[0]["Q1"] == 1
    assert data[1]["Q4"] == 3
