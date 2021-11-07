import asyncio
from http import HTTPStatus
from itertools import chain
from typing import List
from uuid import UUID

import httpx

from config.settings import APIKEY, SERVICE_URL, TENANT_ID
from exceptions.custom_exceptions import (
    CommunicationFailedError,
    OrderNotFoundError,
)
from schemas.item import Item


async def _get_package_items(client, order_uuid: UUID, package_uuid: UUID):
    response = client.get(
        url=f"{SERVICE_URL}/orders/{order_uuid}/packages{package_uuid}/items",
        headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
    )
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


async def get_order_items(order_uuid: UUID) -> List[Item]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICE_URL}/orders/{order_uuid}",
                headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
            )
            response.raise_for_status()
            packages = response.json()["packages"]
            items = await asyncio.gather(
                *(
                    _get_package_items(
                        client=client,
                        order_uuid=order_uuid,
                        package_uuid=pkg["uuid"],
                    )
                    for pkg in packages
                )
            )
            return list(chain.from_iterable(items))
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == HTTPStatus.NOT_FOUND:
                raise OrderNotFoundError() from exc
            raise exc
        except httpx.HTTPError as exc:
            raise CommunicationFailedError() from exc
