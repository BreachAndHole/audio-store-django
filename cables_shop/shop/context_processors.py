from .models import *


def get_cart_items_total(request):
    if not request.user.is_authenticated:
        return {'items_in_cart': 0}

    customer = request.user.customer

    order, is_created = Order.objects.get_or_create(customer=customer, is_active=True)
    if is_created or order is None:
        return {'cart_items_total': 0}

    ordered_items = OrderedProduct.objects.filter(order=order)
    items_in_cart = len(ordered_items)

    return {'cart_items_total': items_in_cart}
