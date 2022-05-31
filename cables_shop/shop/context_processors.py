from .models import *


def get_cart_items_total(request):
    if not request.user.is_authenticated:
        return {'items_in_cart': 0}

    order, _ = Order.objects.get_or_create(
        customer=request.user.customer,
        is_active=True
    )

    ordered_items = OrderedProduct.objects.filter(order=order)
    items_in_cart = len(ordered_items)

    return {'cart_items_total': items_in_cart}
