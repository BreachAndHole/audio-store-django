from typing import Optional
from .models import ShippingAddress, Customer, Order


def get_last_used_customer_address(customer: Customer) -> Optional[ShippingAddress]:
    """ Returns last used customer address if exists, otherwise None """
    user_addresses = ShippingAddress.objects.filter(customer=customer)
    if user_addresses.count():
        return user_addresses.last()
    return None


def create_empty_cart(customer: Customer) -> None:
    Order.objects.get_or_create(
        customer=customer,
        status=Order.OrderStatus.IN_CART,
    )
