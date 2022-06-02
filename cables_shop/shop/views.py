from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import list, detail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, CustomerInformationForm
from .utils.cart_utils import process_cart_update
from .utils.checkout_utils import *
from .models import *
from .errors import *


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
        context['cart_total_price'] = Order.objects.get(
            customer=self.request.user.customer,
            status=Order.OrderStatus.IN_CART
        ).get_order_total_price
        return context

    def get_queryset(self):
        return OrderedProduct.objects.filter(
            order__customer=self.request.user.customer,
            order__status=Order.OrderStatus.IN_CART
        ).order_by(
            'date_added'
        )


@login_required(login_url='user_login_page')
def checkout(request):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(
        customer=customer,
        status=Order.OrderStatus.IN_CART,
    )
    ordered_products = order.orderedproduct_set.all()

    # Prefilling checkout form with customer information we have
    form_initial_values = get_customer_form_initials(customer)
    form = CustomerInformationForm(
        request.POST or None, initial=form_initial_values
    )

    if request.method == 'POST' and form.is_valid():
        # Check if the customer want to save his info for further orders
        if 'update_customer_info' in request.POST:
            update_customer_information(
                customer=customer,
                updated_data=form.cleaned_data
            )
        # making this address primary and every else not
        is_new_primary = 'make_address_primary' in request.POST
        if is_new_primary:
            ShippingAddress.objects.filter(
                customer=customer
            ).update(
                is_primary=False
            )

        shipping_address = ShippingAddress.objects.create(
            customer=customer,
            is_primary=is_new_primary,
            address=form.cleaned_data.get('address'),
            city=form.cleaned_data.get('city'),
            state=form.cleaned_data.get('state'),
            zipcode=form.cleaned_data.get('zipcode'),
        )

        shipping_address.save()

        # Check if all ordered cables still in stock
        if is_all_cart_products_in_stock(ordered_products):
            update_cables_quantity_in_stock(ordered_products)
        else:
            correct_cart_products_quantity(ordered_products)
            messages.error(
                request,
                f'Части позиций осталось меньше, чем вы заказали. '
                f'Колличество измененно на максимально возможное'
            )
            return redirect('checkout_page')

        # Changing order status and saving it
        order.shipping_address = shipping_address
        order.status = Order.OrderStatus.ACCEPTED
        order.save()

        # Clean all non valid addresses
        ShippingAddress.objects.filter(
            customer=customer,
            is_primary=False,
            address__isnull=True
        ).delete()

        return redirect('home_page')

    context = {
        'title': 'Оформление заказа',
        'form': form,
        'ordered_products': ordered_products,
        'cart_total_price': order.get_order_total_price,
    }

    return render(request, 'shop/checkout.html', context)


def update_cart(request):
    """
    This view is working with JSON-response sent by cart.js on every
    cart items related button click
    """

    # Double-checking if user is authenticated
    if not request.user.is_authenticated:
        messages.info('Для заказа необходимо войти в аккаунт')
        redirect('user_login_page')
    try:
        process_cart_update(request)
    except JSONResponseParsingError:
        return JsonResponse('Error during parsing response', safe=False)
    except UpdateCartError:
        return JsonResponse('Error during cart update', safe=False)

    return JsonResponse('Cart has been updated', safe=False)


def user_registration(request):
    form = UserRegistrationForm()

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
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

            customer = request.user.customer
            ShippingAddress.objects.get_or_create(
                customer=customer,
                is_primary=True,
            )
            Order.objects.get_or_create(
                customer=customer,
                status=Order.OrderStatus.IN_CART,
            )

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
    customer = request.user.customer
    try:
        primary_address = customer.shipping_address.get(is_primary=True)
    except Exception:
        raise NotImplementedError

    contex = {
        'title': 'Личный кабинет',
        'customer': customer,
        'address': primary_address,
        'orders': Order.objects.filter(
            customer=customer
        ).exclude(
            status=Order.OrderStatus.IN_CART
        ).order_by(
            '-pk'
        ),
    }
    return render(request, 'shop/user_profile.html', contex)


@login_required(login_url='user_login_page')
def order_information(request, order_pk: int):
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


@login_required(login_url='user_login_page')
def user_profile_update(request):
    contex = {
        'title': 'Обновление профиля',
    }
    return render(request, 'shop/user_profile_update.html', contex)
