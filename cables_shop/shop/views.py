from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
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
from .models import CablePhoto, CableType, Cable, Order, OrderedProduct
from shop import config


class IndexPageView(list.ListView):
    """ Home page with cable types displayed on it"""
    model = CableType
    context_object_name = 'cable_types'
    template_name = 'shop/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.INDEX_PAGE_TITLE
        return context


class AllCablesPageView(list.ListView):
    """
    All cables for sale is displayed on this page.
    Cables are queried via related title photos
    """
    model = CablePhoto
    context_object_name = 'photos'
    template_name = 'shop/all_cables.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.ALL_CABLES_PAGE_TITLE
        return context

    def get_queryset(self):
        # Showing on the page only cables marked as for sale
        title_photos = CablePhoto.objects.filter(
            is_title=True,
            cable__is_for_sale=True,
        ).select_related('cable').select_related('cable__type')
        return title_photos


class CablePageView(detail.DetailView):
    """ Detailed page for each cable """
    model = Cable
    context_object_name = 'cable'
    slug_url_kwarg = 'cable_slug'
    template_name = 'shop/cable.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Hi-Fi store - {context.get("cable").name}'
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
        ordered_products = OrderedProduct.objects.filter(
            order__customer=self.request.user,
            order__status=Order.OrderStatus.IN_CART
        )
        if not ordered_products:
            return redirect('all_cables_page')
        return super(CartPageView, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.CART_PAGE_TITLE
        return context

    def get_queryset(self):
        # Getting only products in cart for this customer
        ordered_products = OrderedProduct.objects.filter(
            order__customer=self.request.user,
            order__status=Order.OrderStatus.IN_CART
        ).order_by('date_added').select_related('product')
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
        except ShippingAddressNotProvidedError:
            messages.error(
                request,
                'При выборе доставки необходимо указать хотя бы адрес и город.'
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
        'title': config.CHECKOUT_PAGE_TITLE,
        'form': form,
        'ordered_products': checkout_service.ordered_products,
        'delivery_price': config.DELIVERY_PRICE,
    }
    return render(request, 'shop/checkout.html', context)


def update_cart(request: HttpRequest):
    """
    This view is working with JSON-response sent by cart.js on every
    cart items related button click (add, remove, delete)
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
        messages.success(self.request, f'Аккаунт {user_name} создан успешно.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # sent error message to user
        messages.error(self.request, 'Ошибка при регистрации. Повторите попытку.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.REGISTRATION_PAGE_TITLE
        return context


def user_login(request: HttpRequest):
    contex = {
        'title': config.LOGIN_PAGE_TITLE,
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.USER_PROFILE_PAGE_TITLE
        context['last_used_address'] = utils.get_last_used_customer_address(
            self.request.user
        )
        return context

    def get_queryset(self):
        checked_out_customer_orders = Order.objects.filter(
            customer=self.request.user
        ).exclude(status=Order.OrderStatus.IN_CART).order_by('-pk')
        return checked_out_customer_orders


class OrderView(LoginRequiredMixin, detail.DetailView):
    login_url = 'user_login_page'
    model = Order
    context_object_name = 'order'
    pk_url_kwarg = 'order_pk'
    template_name = 'shop/order_info.html'

    def get(self, *args, **kwargs):
        """
        If user tries to access other user order
        or the order is not checked out he must be redirected
        """
        order = self.get_object()
        is_in_cart = order.status == Order.OrderStatus.IN_CART
        if order.customer != self.request.user or is_in_cart:
            return redirect('user_profile_page')

        return super(OrderView, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Hi-Fi store - Заказ №{self.object.pk}'
        context['delivery_price'] = config.DELIVERY_PRICE

        order = self.get_object()
        context['ordered_products'] = order.orderedproduct_set.select_related('product')
        return context


class AboutPageView(TemplateView):
    template_name = 'shop/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = config.ABOUT_PAGE_TITLE
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
        'title': config.UPDATE_USER_INFO_PAGE_TITLE,
        'form': form
    }
    return render(request, 'shop/update_user_info.html', contex)
