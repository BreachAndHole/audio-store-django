from typing import TypedDict
from django.db.models import F
from shop.models import *


class CustomerFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


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
