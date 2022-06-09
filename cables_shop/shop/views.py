from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView, list, detail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .services import CartUpdateService, UserInformationService
from .errors import *
from . import utils
from .models import CableType, Cable, Order, OrderedProduct
from cables_shop.settings import DELIVERY_PRICE


class IndexPageView(list.ListView):
    """ Home page with cable types displayed on it"""
    model = CableType
    context_object_name = 'cable_types'
    template_name = 'shop/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class AllCablesPageView(list.ListView):
    """ All cables for sale is displayed on this page """
    model = Cable
    context_object_name = 'cables'
    template_name = 'shop/all_cables.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Товары'
        return context

    def get_queryset(self):
        # Showing on the page only cables marked as for sale
        return Cable.objects.filter(is_for_sale=True)


class CablePageView(detail.DetailView):
    """ Detailed page for each cable """
    model = Cable
    context_object_name = 'cable'
    slug_url_kwarg = 'cable_slug'
    template_name = 'shop/cable.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Страница товара - {context.get("cable").name}'
        return context


class CartPageView(LoginRequiredMixin, list.ListView):
    """
    Cart page. Can only be accessed by logged in users
    with at least one item in cart
    """
    login_url = 'user_login_page'
    model = OrderedProduct
    context_object_name = 'ordered_products'
    template_name = 'shop/cart.html'

    def get(self, *args, **kwargs):
        """ Redirect user if he tries to access empty cart """
        ordered_products = Order.objects.get(
            customer=self.request.user,
            status=Order.OrderStatus.IN_CART
        ).orderedproduct_set.all()
        if not ordered_products:
            return redirect('all_cables_page')
        return super(CartPageView, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'

        # Adding cart total price to context
        products = context['ordered_products']
        products_total_price = sum(product.total_price for product in products)
        context['products_total_price'] = products_total_price
        return context

    def get_queryset(self):
        # Getting only products in cart for this customer
        ordered_products = OrderedProduct.objects.filter(
            order__customer=self.request.user,
            order__status=Order.OrderStatus.IN_CART
        ).order_by('date_added')
        return ordered_products


@login_required(login_url='user_login_page')
def checkout(request: HttpRequest):
    checkout_service = UserInformationService(request.user, request.POST)

    # Redirect user if his cart is empty
    if not checkout_service.ordered_products:
        return redirect('all_cables_page')

    form = checkout_service.form
    if request.method == 'POST' and form.is_valid():
        try:
            checkout_service.process_checkout()
        except PhoneNumberAlreadyExistsError:
            messages.error(
                request,
                'Пользователь с таким номером телефона уже зарегистрирован. '
                'Используйте телефон, указанный при регистрации или введите другой.'
            )
            return redirect('checkout_page')
        except ProductsQuantityError:
            checkout_service.correct_ordered_products()
            messages.error(
                request,
                'Количество некоторых товаров в наличии изменилось. '
                'Корзина была обновлена. Пожалуйста повторите отправку заказа.'
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
    except JSONResponseParsingError:
        return JsonResponse('Error during parsing response', safe=False)
    except CartUpdateError:
        return JsonResponse('Error during cart update', safe=False)

    return JsonResponse('Cart has been updated', safe=False)


class UserRegistrationView(FormView):
    form_class = UserRegistrationForm
    template_name = 'shop/registration.html'
    success_url = reverse_lazy('user_login_page')

    def form_valid(self, form):
        form.save()
        # sent success message to user
        user_name = form.cleaned_data.get('email', '')
        messages.success(self.request, f'Аккаунт {user_name} создан успешно')
        return super().form_valid(form)


def user_login(request: HttpRequest):
    contex = {
        'title': 'Войти в аккаунт',
    }
    if request.method != 'POST':
        return render(request, 'shop/login.html', contex)

    email = request.POST.get('email_field', None)
    password = request.POST.get('password_field', None)
    user = authenticate(request, username=email, password=password)
    if user is None:
        messages.info(
            request,
            'Электронная почта или пароль введены неверно'
        )
        return render(request, 'shop/login.html', contex)

    login(request, user)
    # create empty cart if user has no cart
    utils.create_empty_cart(request.user)
    return redirect('home_page')


class UserLogoutView(LoginRequiredMixin, RedirectView):
    login_url = 'user_login_page'
    pattern_name = 'home_page'

    def get(self, *args, **kwargs):
        logout(self.request)
        return super(UserLogoutView, self).get(*args, **kwargs)


class UserProfileView(LoginRequiredMixin, list.ListView):
    login_url = 'user_login_page'
    model = Order
    context_object_name = 'orders'
    template_name = 'shop/user_profile.html'

    def get_queryset(self):
        checked_out_customer_orders = Order.objects.filter(
            customer=self.request.user
        ).exclude(status=Order.OrderStatus.IN_CART).order_by('-pk')
        return checked_out_customer_orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Личный кабинет'
        context['last_used_address'] = utils.get_last_used_customer_address(
            self.request.user
        )
        return context


class OrderView(LoginRequiredMixin, detail.DetailView):
    login_url = 'user_login_page'
    model = Order
    context_object_name = 'order'
    pk_url_kwarg = 'order_pk'
    template_name = 'shop/order_info.html'

    def get(self, *args, **kwargs):
        order = self.get_object()
        if order.customer != self.request.user or order.status == Order.OrderStatus.IN_CART:
            return redirect('user_profile_page')

        return super(OrderView, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Заказ №{self.object.pk}'
        return context


class AboutPageView(TemplateView):
    template_name = 'shop/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Обо мне'
        return context


def update_user_info(request: HttpRequest):
    update_info_service = UserInformationService(request.user, request.POST)
    form = update_info_service.form

    if request.method == 'POST' and form.is_valid():
        try:
            update_info_service.process_information_update()
        except PhoneNumberAlreadyExistsError:
            messages.error(
                request,
                'Пользователь с таким номером телефона уже зарегистрирован.'
            )
            return redirect('update_user_info_page')

        return redirect('user_profile_page')

    contex = {
        'title': f'Обновление информации',
        'form': form
    }
    return render(request, 'shop/update_user_info.html', contex)
