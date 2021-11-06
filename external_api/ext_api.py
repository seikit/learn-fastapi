from http import HTTPStatus
from typing import List
from uuid import UUID

import httpx

from config.settings import SERVICE_URL, APIKEY, TENANT_ID
from exceptions.custom_exceptions import OrderNotFoundError, CommunicationFailedError
from schemas.item import Item


def _get_package_items(order_uuid, package_uuid):
    response = httpx.get(
        url=f"{SERVICE_URL}/orders/{order_uuid}/packages/{package_uuid}/items",
        headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID}
    )
    response.raise_for_status()
    return [
        Item(
            sku=item["product"]["code"],
            description=item["product"].get("description", ""),
            image_url=item["product"].get("image_url", ""),
            reference=item["product"].get("reference", ""),
            quantity=item["quantity"],
        )
        for item in response.json()
    ]


def get_order_items(order_uuid: UUID) -> List[Item]:
    try:
        response = httpx.get(
            url=f"{SERVICE_URL}/orders/{order_uuid}",
            headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID}
        )
        response.raise_for_status()
        packages = response.json()['packages']
        items = []
        for pkg in packages:
            items.extend(
                _get_package_items(order_uuid, pkg['uuid'])
            )
        return items
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == HTTPStatus.NOT_FOUND:
            raise OrderNotFoundError() from exc
        raise exc
    except httpx.HTTPError as exc:
        raise CommunicationFailedError() from exc
