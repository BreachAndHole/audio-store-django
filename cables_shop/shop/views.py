import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import list, detail, TemplateView
from django.db.models import F
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *


class IndexPageView(list.ListView):
    model = CableType
    context_object_name = 'cable_types'
    template_name = 'shop/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class AllCablesPageView(list.ListView):
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


class CablePageView(detail.DetailView):
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
    context = {
        'title': f'Корзина',
    }
    return render(request, 'shop/cart.html', context)


class CheckoutPageView(TemplateView):
    template_name = 'shop/checkout.html'
    extra_context = {
        'title': f'Оформление заказа',
    }


def user_registration(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user_name = form.cleaned_data.get('username', '')
            messages.success(request, f'Аккаунт пользователя {user_name} создан')

            return redirect('user_login_page')

    contex = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'shop/registration.html', contex)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username_field', '')
        password = request.POST.get('password_field', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.info(request, 'Имя пользователя или пароль введены неверно')
        else:
            login(request, user)
            return redirect('home_page')

    contex = {
        'title': 'Войти в аккаунт',
    }
    return render(request, 'shop/login.html', contex)


def user_logout(request):
    logout(request)
    return redirect('user_login_page')
