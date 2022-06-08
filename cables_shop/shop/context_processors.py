from typing import TypedDict
from .models import *
from django.http import HttpRequest


class CartItemsTotalData(TypedDict):
    cart_items_total: int


def get_cart_items_total(request: HttpRequest) -> CartItemsTotalData:
    if not request.user.is_authenticated:
        return {'cart_items_total': 0}
    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        status=Order.OrderStatus.IN_CART,
    )
    ordered_items = OrderedProduct.objects.filter(order=order)
    items_total = sum(item.quantity for item in ordered_items)
    return {'cart_items_total': items_total}
