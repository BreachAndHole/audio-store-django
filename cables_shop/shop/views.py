import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import list, detail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import RegisterUserForm, CheckoutForm
from .utils import *
from .models import *


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Товары'
        context['cable_types'] = CableType.objects.all()

        cable_prices = [cable.price for cable in context.get('cables', [])]
        context['min_price'] = min(cable_prices)
        context['max_price'] = max(cable_prices)
        return context


class CablePageView(detail.DetailView):
    model = Cable
    context_object_name = 'cable'
    slug_url_kwarg = 'cable_slug'
    template_name = 'shop/cable.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Страница товара - {context.get("cable").name}'
        return context


class CartPageView(LoginRequiredMixin, list.ListView):
    login_url = 'user_login_page'
    model = OrderedProduct
    context_object_name = 'ordered_products'
    template_name = 'shop/cart.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'

        ordered_products = context.get('ordered_products', [])
        cart_total_price = sum([product.get_product_total_price for product in ordered_products])
        context['cart_total_price'] = cart_total_price
        return context

    def get_queryset(self):
        return OrderedProduct.objects.filter(
            order__customer=self.request.user.customer,
            order__is_active=True
        ).order_by(
            'date_added'
        )


@login_required(login_url='user_login_page')
def checkout(request):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    order = Order.objects.get(customer=customer, is_active=True)
    ordered_products = order.orderedproduct_set.all()

    form_initial_values = get_checkout_form_initials(customer=customer)
    form = CheckoutForm(request.POST or None, initial=form_initial_values)

    if request.method == 'POST' and form.is_valid():
        update_customer_information(
            customer=customer,
            updated_data=form.cleaned_data
        )
        order.is_active = False
        order.save()

        for product in ordered_products:
            cable = Cable.objects.get(pk=product.product.pk)
            cable.units_in_stock -= product.quantity
            cable.save()

        return redirect('home_page')

    context = {
        'title': 'Оформление заказа',
        'form': form,
        'ordered_products': ordered_products,
        'cart_total_price': order.get_cart_total_price,
    }

    return render(request, 'shop/checkout.html', context)


def update_cart(request):
    try:
        cart_update_received_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse('Cart has not been updated', safe=False)

    product_id = cart_update_received_data.get('productId', None)
    action = cart_update_received_data.get('action', None)
    if product_id is None or action is None:
        return JsonResponse('Cart has not been updated', safe=False)

    update_ordered_product(request, product_id, action)

    return JsonResponse('Cart has been updated', safe=False)


def user_registration(request):
    form = RegisterUserForm()

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()

            user_name = form.cleaned_data.get('username', '')
            messages.success(request, f'Аккаунт {user_name} создан')

            return redirect('user_login_page')

    contex = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'shop/registration.html', contex)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username_field', None)
        password = request.POST.get('password_field', None)
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.info(
                request,
                'Имя пользователя или пароль введены неверно'
            )
        else:
            login(request, user)
            return redirect('home_page')

    contex = {
        'title': 'Войти в аккаунт',
    }
    return render(request, 'shop/login.html', contex)


def user_logout(request):
    logout(request)
    return redirect('home_page')


@login_required(login_url='user_login_page')
def user_profile(request):
    contex = {
        'title': 'Личный кабинет',
        'customer': request.user.customer,
    }
    return render(request, 'shop/user_profile.html', contex)
