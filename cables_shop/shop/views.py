from django.shortcuts import render
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
