from typing import List

from django.db.models import F
from django.http import HttpRequest
from .models import *


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
        ordered_products: List[OrderedProduct]
) -> bool:
    for product in ordered_products:
        ordered_cable: Cable = Cable.objects.get(pk=product.product.pk)
        if ordered_cable.units_in_stock < product.quantity:
            return False

    return True


def update_cables_quantity_in_stock(
        ordered_products: List[OrderedProduct]
) -> None:
    for product in ordered_products:
        ordered_cable = Cable.objects.get(pk=product.product.pk)
        ordered_cable.units_in_stock = F('units_in_stock') - product.quantity
        ordered_cable.save()


def get_checkout_form_initials(customer: Customer) -> dict:
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
