from .models import *
from django.http import HttpRequest


def get_cart_items_total(request: HttpRequest) -> dict[str, int]:
    if not request.user.is_authenticated:
        return {'items_in_cart': 0}
    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        status=Order.OrderStatus.IN_CART,
    )
    ordered_items = OrderedProduct.objects.filter(order=order)
    items_total = sum(item.quantity for item in ordered_items)
    return {'cart_items_total': items_total}
