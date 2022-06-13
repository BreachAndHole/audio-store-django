from typing import TypedDict
from .models import Order, OrderedProduct
from django.http import HttpRequest


class CartItemsTotalData(TypedDict):
    cart_items_total: int


def get_cart_items_total(request: HttpRequest) -> CartItemsTotalData:
    if not request.user.is_authenticated:
        return {'cart_items_total': 0}

    ordered_products = OrderedProduct.objects.select_related('order').filter(
        order__customer=request.user,
        order__status=Order.OrderStatus.IN_CART
    ).values('quantity')

    items_total = sum(item['quantity'] for item in ordered_products)
    return {'cart_items_total': items_total}
