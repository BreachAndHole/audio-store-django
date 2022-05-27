import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import list, detail
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
    else:
        # Kostyl'
        order = {'get_cart_total_price': 0, 'get_cart_total_amount': 0}
        all_items = []

    context = {
        'title': f'Корзина',
        'all_items': all_items,
        'order': order,
    }
    return render(request, 'shop/cart.html', context)


def checkout(request):
    context = {
        'title': f'Оформление заказа',
    }
    return render(request, 'shop/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    print(data)
    # item_id = data["itemId"]
    action = data["action"]
    # print(f'{item_id = }')
    print(f'{action = }')
    return JsonResponse('Item was added', safe=False)
