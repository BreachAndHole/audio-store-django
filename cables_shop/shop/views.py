from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *


def index(request):
    context = {
        'title': 'Главная страница',
        'cable_types': CableType.objects.all(),
    }
    return render(request, 'shop/index.html', context)


def all_cables(request):
    context = {
        'title': 'Товары',
        'cable_types': CableType.objects.all(),
        'cables': Cable.objects.all(),
    }
    return render(request, 'shop/all_cables.html', context)


def cable_page(request, cable_slug):
    cable = get_object_or_404(Cable, slug=cable_slug)
    context = {
        'title': f'Страница товара - {cable.name}',
        'cable': cable,
    }
    return render(request, 'shop/cable.html', context)
