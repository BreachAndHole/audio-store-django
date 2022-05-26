from django.shortcuts import render
from django.views.generic import list, detail
from .models import *


class IndexPage(list.ListView):
    model = CableType
    context_object_name = 'cable_types'
    template_name = 'shop/index.html'
    extra_context = {
        'title': 'Главная страница',
    }


class AllCablesPage(list.ListView):
    model = Cable
    context_object_name = 'cables'
    template_name = 'shop/all_cables.html'
    extra_context = {
        'title': 'Товары',
        'cable_types': CableType.objects.all(),
    }


class CablePage(detail.DetailView):
    model = Cable
    context_object_name = 'cable'
    slug_url_kwarg = 'cable_slug'
    template_name = 'shop/cable.html'
    extra_context = {
        'title': f'Страница товара',
    }


def cart(request):
    context = {
        'title': f'Корзина',
    }
    return render(request, 'shop/cart.html', context)
