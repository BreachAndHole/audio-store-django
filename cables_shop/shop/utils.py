from typing import TypedDict
from django.db.models import F
from django.http import HttpRequest
from .models import *


class CustomerFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


def update_ordered_product_in_cart(
    request: HttpRequest,
    product_id: int,
    action: str
) -> None:
    """This function add, remove and delete products from cart"""
    product = Cable.objects.get(pk=product_id)
    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        status=Order.OrderStatus.IN_CART,
    )

    ordered_product, _ = OrderedProduct.objects.get_or_create(
        order=order,
        product=product
    )

    match action:
        case 'add_to_cart':
            if ordered_product.quantity < product.units_in_stock:
                ordered_product.quantity += 1
        case 'remove_from_cart':
            ordered_product.quantity -= 1
        case 'delete_from_cart':
            ordered_product.quantity = 0

    ordered_product.save()

    if ordered_product.quantity <= 0:
        ordered_product.delete()


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


def get_checkout_form_initials(customer: Customer) -> CustomerFormInitials:
    """
    This function forming a dict of initial values
    for customer information form
    """
    initials = {
        'first_name': customer.first_name or '',
        'last_name': customer.last_name or '',
        'phone': customer.phone or '',
        'address': customer.shipping_address.address or '',
        'city': customer.shipping_address.city or '',
        'state': customer.shipping_address.state or '',
        'zipcode': customer.shipping_address.zipcode or '',
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
    customer.shipping_address.address = updated_data.get('address', '')
    customer.shipping_address.city = updated_data.get('city', '')
    customer.shipping_address.state = updated_data.get('state', '')
    customer.shipping_address.zipcode = updated_data.get('zipcode', '')
    customer.save()
    customer.shipping_address.save()
