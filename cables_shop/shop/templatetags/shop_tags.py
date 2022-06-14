from django import template
from django.db.models.query import QuerySet
from shop.models import CableType, OrderedProduct, Order


register = template.Library()


@register.simple_tag
def get_all_cable_types():
    return CableType.objects.all().order_by('pk')


@register.simple_tag
def product_total_price(quantity: int, price: int) -> int:
    return quantity * price


@register.simple_tag
def cart_items_total(user) -> int:
    """ Calculate ordered items total count"""
    if not user.is_authenticated:
        return 0
    ordered_products = OrderedProduct.objects.select_related('order').filter(
        order__customer=user,
        order__status=Order.OrderStatus.IN_CART
    ).values('quantity')
    items_total = sum(item['quantity'] for item in ordered_products)
    return items_total


@register.simple_tag
def cart_price_total(products: QuerySet[OrderedProduct]) -> int:
    """ Calculate total price for an order without delivery"""
    return sum([product.quantity*product.product.price for product in products])
