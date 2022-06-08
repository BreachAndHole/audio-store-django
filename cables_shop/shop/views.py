from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import list, detail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .services.orders import CartUpdateService, CheckoutService
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

        # Adding cart total price to context
        context['products_total_price'] = Order.objects.get(
            customer=self.request.user.customer,
            status=Order.OrderStatus.IN_CART
        ).products_total_price
        return context

    def get_queryset(self):
        return OrderedProduct.objects.filter(
            order__customer=self.request.user.customer,
            order__status=Order.OrderStatus.IN_CART
        ).order_by('date_added')


@login_required(login_url='user_login_page')
def checkout(request: HttpRequest):
    checkout_service = CheckoutService(request.user.customer, request.POST)
    form = checkout_service.checkout_form

    if request.method == 'POST' and form.is_valid():
        try:
            checkout_service.process_checkout()
        except checkout_service.ProductsQuantityError:
            checkout_service.correct_ordered_products()
            messages.error(
                request,
                'Количетсво некоторых товаров в наличии изменилось. '
                'Корзина была обновлена. Пожалуйста повторите отправку заказа'
            )
            return redirect('checkout_page')
        return redirect('home_page')

    context = {
        'title': 'Оформление заказа',
        'form': form,
        'ordered_products': checkout_service.ordered_products,
        'delivery_price': DELIVERY_PRICE,
        'order_total_price': checkout_service.order.order_total_price,
        'cart_total_price': checkout_service.order.products_total_price,
    }
    return render(request, 'shop/checkout.html', context)


def update_cart(request: HttpRequest):
    """
    This view is working with JSON-response sent by cart.js on every
    cart items related button click
    """
    try:
        CartUpdateService(request).process_cart_update()
    except CartUpdateService.JSONResponseParsingError:
        return JsonResponse('Error during parsing response', safe=False)
    except CartUpdateService.CartUpdateError:
        return JsonResponse('Error during cart update', safe=False)

    return JsonResponse('Cart has been updated', safe=False)


def user_registration(request: HttpRequest):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # sent success message to user
        user_name = form.cleaned_data.get('username', '')
        messages.success(request, f'Аккаунт {user_name} создан успешно')
        return redirect('user_login_page')

    contex = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'shop/registration.html', contex)


def user_login(request: HttpRequest):
    contex = {
        'title': 'Войти в аккаунт',
    }
    if request.method != 'POST':
        return render(request, 'shop/login.html', contex)

    username = request.POST.get('username_field', None)
    password = request.POST.get('password_field', None)
    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.info(
            request,
            'Имя пользователя или пароль введены неверно'
        )
        return render(request, 'shop/login.html', contex)

    login(request, user)

    # create empty cart if user has no cart
    customer = request.user.customer
    Order.objects.get_or_create(
        customer=customer,
        status=Order.OrderStatus.IN_CART,
    )
    return redirect('home_page')


@login_required(login_url='user_login_page')
def user_logout(request):
    logout(request)
    return redirect('home_page')


class UserProfileView(LoginRequiredMixin, list.ListView):
    login_url = 'user_login_page'
    model = Order
    context_object_name = 'orders'
    template_name = 'shop/user_profile.html'

    def get_queryset(self):
        customer_orders = Order.objects.filter(
            customer=self.request.user.customer
        ).exclude(
            status=Order.OrderStatus.IN_CART
        ).order_by('-pk')
        return customer_orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Личный кабинет'
        return context


@login_required(login_url='user_login_page')
def order_information(request: HttpRequest, order_pk: int):
    customer = request.user.customer
    order = get_object_or_404(Order, pk=order_pk)

    # If order don't belong to current user or the order still in cart
    if order.customer != customer or order.status == Order.OrderStatus.IN_CART:
        return redirect('home_page')

    contex = {
        'title': f'Заказ №{order.pk}',
        'order': order,
    }
    return render(request, 'shop/order_info.html', contex)
