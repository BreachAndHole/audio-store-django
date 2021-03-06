from typing import Optional

from .models import Order, OrderedProduct, ShippingAddress, User


def get_last_used_customer_address(customer: User) -> Optional[ShippingAddress]:
    """ Returns last used customer address if exists, otherwise None """
    return ShippingAddress.objects.filter(customer=customer).last()


def create_empty_cart(customer: User) -> None:
    Order.objects.get_or_create(
        customer=customer,
        status=Order.OrderStatus.IN_CART,
    )


def save_or_delete_ordered_product(ordered_product: OrderedProduct) -> None:
    if ordered_product.quantity <= 0:
        ordered_product.delete()
    else:
        ordered_product.save()
