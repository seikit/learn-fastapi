from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from exceptions.custom_exceptions import OrderNotFoundError, CommunicationFailedError
from schemas.item import Item

app = FastAPI()


@app.exception_handler(OrderNotFoundError)
def handle_order_not_found_error(request: Request, exc: OrderNotFoundError):
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"message": "Order not found"})


@app.exception_handler(CommunicationFailedError)
def handle_communication_error(request: Request, exc: CommunicationFailedError):
    return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content={"message": "Service communication failed"})


@app.get('/health')
async def health_check():
    return {'status': 'ok'}


def get_order_items(uuid: UUID) -> List[Item]:
    pass


@app.get('/orders/{uuid}/items')
def read_items(items: List[Item] = Depends(get_order_items)):
    return items
