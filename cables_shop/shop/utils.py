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
            ordered_product.quantity += 1
        case 'remove_from_cart':
            ordered_product.quantity -= 1
        case 'delete_from_cart':
            ordered_product.quantity = 0

    ordered_product.save()

    if ordered_product.quantity <= 0:
        ordered_product.delete()
