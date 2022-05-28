import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import list, detail, TemplateView
from django.db.models import F
from django.contrib import messages
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
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_made=False)
        all_items = order.ordereditem_set.all().order_by('pk')
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


class CheckoutPageView(TemplateView):
    template_name = 'shop/checkout.html'
    extra_context = {
        'title': f'Оформление заказа',
    }


def update_item(request):
    """Update cart function"""
    received_data = json.loads(request.body)
    item_id = received_data["itemId"]
    action = received_data["action"]

    customer = request.user.customer
    item = Cable.objects.get(pk=item_id)
    order, created = Order.objects.get_or_create(customer=customer, is_made=False)
    ordered_item, _ = OrderedItem.objects.get_or_create(order=order, item=item)

    if action == 'add_to_cart':
        ordered_item.amount = F('amount') + 1
    elif action == 'remove_from_cart':
        ordered_item.amount = F('amount') - 1

    ordered_item.save()
    OrderedItem.objects.filter(amount__lte=0).delete()

    return JsonResponse('Date received', safe=False)


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
    contex = {
        'title': 'Войти в аккаунт',
    }
    return render(request, 'shop/login.html', contex)
