from typing import List
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus

from exceptions.order_exception import OrderNotFoundError
from orders_api.api import app, get_order_items
from schemas.item import Item


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def overrides_get_order_items():
    def _overrides_get_order_items(items_or_error):
        def duble(uuid: UUID) -> List[Item]:
            if isinstance(items_or_error, Exception):
                raise items_or_error
            return items_or_error
        app.dependency_overrides[get_order_items] = duble
    yield _overrides_get_order_items
    app.dependency_overrides.clear()


class TestHealthCheck:
    def test_system_health(self, client):
        response = client.get('/health')
        assert response.status_code == HTTPStatus.OK

    def test_response_in_json_format(self, client):
        response = client.get('/health')
        assert response.headers['Content-type'] == 'application/json'

    def test_response_with_content(self, client):
        response = client.get('/health')
        assert response.json() == {
            'status': 'ok'
        }


class TestReadOrders:
    def test_get_order_items_with_invalid_uuid(self, client):
        response = client.get('/orders/wrong-uuid/items')
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_orders_items_from_non_existent_order(self, client, overrides_get_order_items):
        overrides_get_order_items(OrderNotFoundError())
        response = client.get('/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items')
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_order_items_from_valid_order_return_ok(self, client, overrides_get_order_items):
        overrides_get_order_items([])
        response = client.get('/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items')
        assert response.status_code == HTTPStatus.OK

    def test_get_order_items_from_valid_order(self, client, overrides_get_order_items):
        items = [
            Item(sku='1', description='Item 1', image_url='http://url.com/img1', reference='ref1', quantity=1),
            Item(sku='2', description='Item 2', image_url='http://url.com/img2', reference='ref2', quantity=2),
        ]

        overrides_get_order_items(items)
        response = client.get('/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items')
        assert response.json() == items
