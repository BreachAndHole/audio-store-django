from django.http import HttpRequest
from .models import *


def update_ordered_product(request: HttpRequest, product_id: int, action: str) -> None:
    product = Cable.objects.get(pk=product_id)
    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        is_active=True
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


def get_checkout_form_initials(customer: Customer) -> dict:
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


def update_customer_information(customer: Customer, updated_data: dict) -> None:
    customer.first_name = updated_data.get('first_name', '')
    customer.last_name = updated_data.get('last_name', '')
    customer.phone = updated_data.get('phone', '')
    customer.shipping_address.address = updated_data.get('address', '')
    customer.shipping_address.city = updated_data.get('city', '')
    customer.shipping_address.state = updated_data.get('state', '')
    customer.shipping_address.zipcode = updated_data.get('zipcode', '')
    customer.save()
    customer.shipping_address.save()
