import json
from enum import Enum
from typing import NamedTuple
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from shop.errors import *
from shop.models import *


class UpdateCartAction(Enum):
    ADD_TO_CART = 'add_to_cart'
    REMOVE_FROM_CART = 'remove_from_cart'
    DELETE_FROM_CART = 'delete_from_cart'


class CartUpdateParsedData(NamedTuple):
    product_id: int
    action: str


def process_cart_update(request: HttpRequest) -> None:
    parsed_response = _parse_json_update_data(request)
    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        status=Order.OrderStatus.IN_CART,
    )
    ordered_product = _get_product_to_update(
        order,
        parsed_response.product_id
    )
    _update_product_quantity_in_cart(
        ordered_product,
        parsed_response.action
    )
    _save_or_delete_product_in_cart(ordered_product)


def _parse_json_update_data(request: HttpRequest) -> CartUpdateParsedData:
    """
    This function is parsing json response from cart.js script.
    """
    try:
        received_data = json.loads(request.body)
    except json.JSONDecodeError:
        raise JSONResponseParsingError('Error during json response decoding')

    try:
        parsed_data = CartUpdateParsedData(
            product_id=received_data.get('productId'),
            action=received_data.get('action')
        )
    except KeyError:
        raise JSONResponseParsingError(
            'productId or action is not in response'
        )

    return parsed_data


def _get_product_to_update(
        order: Order,
        product_id: int
) -> OrderedProduct:
    """Getting or creating new ordered product for further updating"""
    try:
        cable = Cable.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        raise UpdateCartError(
            f'There is no product with {product_id=}'
        )

    ordered_product, _ = OrderedProduct.objects.get_or_create(
        order=order,
        product=cable
    )
    return ordered_product


def _update_product_quantity_in_cart(
        ordered_product: OrderedProduct,
        action: str
) -> None:
    """This function is changing quantity of product needed to update"""
    match action:
        case UpdateCartAction.ADD_TO_CART.value:
            if ordered_product.quantity < ordered_product.product.units_in_stock:
                ordered_product.quantity += 1
        case UpdateCartAction.REMOVE_FROM_CART.value:
            ordered_product.quantity -= 1
        case UpdateCartAction.DELETE_FROM_CART.value:
            ordered_product.quantity = 0
        case _:
            raise UpdateCartError(f'Undefined {action = }')


def _save_or_delete_product_in_cart(ordered_product: OrderedProduct) -> None:
    if ordered_product.quantity <= 0:
        ordered_product.delete()
    else:
        ordered_product.save()
