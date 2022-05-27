from .models import *


def get_cart_items_total(request):
    if not request.user.is_authenticated:
        return {'cart_items_total': 0}

    customer = request.user.customer

    order = Order.objects.get(customer=customer, is_made=False)

    if not order:
        return {'cart_items_total': 0}

    ordered_items = OrderedItem.objects.filter(order=order)
    cart_items_total = sum([item.amount for item in ordered_items])

    return {'cart_items_total': cart_items_total}
