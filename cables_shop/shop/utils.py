import json
from enum import Enum
from typing import TypedDict, NamedTuple
from django.db.models import F
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from .errors import *
from .models import *


class CustomerFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


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


def is_all_cart_products_in_stock(
        ordered_products: list[OrderedProduct]
) -> bool:
    """
    This function checks if in stock are still
    enough products to process the order.
    It's made for a situations when one customer is filling the card
    and at the same time another customer bought all the cables first one need
    """
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        if cable.units_in_stock < ordered_product.quantity:
            return False

    return True


def update_cables_quantity_in_stock(
        ordered_products: list[OrderedProduct]
) -> None:
    """This function updates in stock quantity of ordered cables"""
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        cable.units_in_stock = F('units_in_stock') - ordered_product.quantity
        cable.save()


def correct_cart_products_quantity(
        ordered_products: list[OrderedProduct]
) -> None:
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        if ordered_product.quantity > cable.units_in_stock:
            ordered_product.quantity = cable.units_in_stock
            ordered_product.save()


def get_customer_form_initials(customer: Customer) -> CustomerFormInitials:
    """
    This function forming a dict of initial values
    for customer information form
    """
    primary_shipping_address = get_customer_primary_address(customer)

    initials = {
        'first_name': customer.first_name or '',
        'last_name': customer.last_name or '',
        'phone': customer.phone or '',
        'address': primary_shipping_address.address or '',
        'city': primary_shipping_address.city or '',
        'state': primary_shipping_address.state or '',
        'zipcode': primary_shipping_address.zipcode or '',
    }
    return initials


def update_customer_information(
        customer: Customer,
        updated_data: dict
) -> None:
    """This function update customer info with data from customer info form"""
    customer.first_name = updated_data.get('first_name', '')
    customer.last_name = updated_data.get('last_name', '')
    customer.phone = updated_data.get('phone', '')
    customer.save()


def get_customer_primary_address(customer: Customer) -> ShippingAddress:
    try:
        primary_shipping_address = ShippingAddress.objects.get(
            customer=customer,
            is_primary=True,
        )
    except Exception:
        raise NotImplementedError

    return primary_shipping_address
