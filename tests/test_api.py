import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus

from orders_api.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_system_health(client):
    response = client.get('/health')
    assert response.status_code == HTTPStatus.OK


def test_response_in_json_format(client):
    response = client.get('/health')
    assert response.headers['Content-type'] == 'application/json'


def test_response_with_content(client):
    response = client.get('/health')
    assert response.json() == {
        'status': 'ok'
    }