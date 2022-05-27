import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import list, detail
from django.db.models import F
from .models import *


class IndexPage(list.ListView):
    model = CableType
    context_object_name = 'cable_types'
    template_name = 'shop/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class AllCablesPage(list.ListView):
    model = Cable
    context_object_name = 'cables'
    template_name = 'shop/all_cables.html'
    extra_context = {
        'title': 'Товары',
        'cable_types': CableType.objects.all(),
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Товары'
        context['cable_types'] = CableType.objects.all()
        return context


class CablePage(detail.DetailView):
    model = Cable
    context_object_name = 'cable'
    slug_url_kwarg = 'cable_slug'
    template_name = 'shop/cable.html'
    extra_context = {
        'title': f'Страница товара',
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Страница товара - {context.get("cable").name}'
        return context


# This needs to be refactored
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_made=False)
        all_items = order.ordereditem_set.all()
        cart_total_items = order.get_cart_total_amount
    else:
        # Kostyl'
        order = {'get_cart_total_price': 0, 'get_cart_total_amount': 0}
        cart_total_items = 0
        all_items = []

    context = {
        'title': f'Корзина',
        'all_items': all_items,
        'order': order,
        # 'cart_counter': cart_total_items,
    }
    return render(request, 'shop/cart.html', context)


def checkout(request):
    context = {
        'title': f'Оформление заказа',
    }
    return render(request, 'shop/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    item_id = data["itemId"]
    action = data["action"]

    customer = request.user.customer
    item = Cable.objects.get(pk=item_id)
    order, created = Order.objects.get_or_create(customer=customer, is_made=False)
    ordered_item, created = OrderedItem.objects.get_or_create(order=order, item=item)

    if action == 'add_to_cart':
        ordered_item.amount += 1
    elif action == 'remove_from__cart':
        ordered_item.amount -= 1

    ordered_item.save()
    if ordered_item.amount < 0:
        ordered_item.delete()

    context = {
        'cart_items_total': order.get_cart_total_amount,
    }
    return JsonResponse(context, safe=False)
