from django.shortcuts import render


def index(request):
    context = {
        'title': 'Главная страница',
    }
    return render(request, 'shop/index.html', context)


def all_cables(request):
    context = {
        'title': 'Товары',
    }
    return render(request, 'shop/all_cables.html', context)
