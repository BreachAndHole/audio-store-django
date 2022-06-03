from typing import TypedDict
from django.db.models import F
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from shop.errors import *
from shop.forms import CustomerInformationForm
from shop.models import *


class CustomerFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


class CheckoutCustomerService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.customer = get_object_or_404(Customer, user=request.user)
        self.ordered_products = OrderedProduct.objects.filter(
            order__customer=self.customer,
            order__status=Order.OrderStatus.IN_CART,
        )
        self.checkout_form = self._get_checkout_form()

    def process_checkout(self):
        self._update_customer_information()
        self._check_quantity_in_stock()
        self._checkout_the_order()
        self._clean_non_valid_addresses()

    def correct_ordered_products_quantity(self) -> None:
        for product in self.ordered_products:
            if product.product.units_in_stock > 0:
                product.quantity = product.product.units_in_stock
                product.save()
            else:
                product.delete()

    def _update_customer_information(self) -> None:
        updated_data = self.checkout_form.cleaned_data
        try:
            self.customer.first_name = updated_data.get('first_name')
            self.customer.last_name = updated_data.get('last_name')
            self.customer.phone = updated_data.get('phone')
        except KeyError:
            raise CustomerInfoUpdateError
        self.customer.save()

    def _check_quantity_in_stock(self) -> None:
        for product in self.ordered_products:
            if product.quantity > product.product.units_in_stock:
                raise NotEnoughProductsInStockError

    def _checkout_the_order(self) -> None:
        order = Order.objects.get(
            customer=self.customer,
            status=Order.OrderStatus.IN_CART
        )
        order.shipping_address = self._get_shipping_address()
        order.status = Order.OrderStatus.ACCEPTED
        order.save()

    def _get_shipping_address(self) -> ShippingAddress:
        ShippingAddress.objects.update(is_primary=False)
        shipping_address = ShippingAddress.objects.get_or_create(
            customer=self.customer,
            address=self.checkout_form.cleaned_data.get('address', ''),
            city=self.checkout_form.cleaned_data.get('city', ''),
            state=self.checkout_form.cleaned_data.get('state', ''),
            zipcode=self.checkout_form.cleaned_data.get('zipcode', ''),
        )
        shipping_address.save()
        return shipping_address

    def _get_checkout_form(self) -> CustomerInformationForm:
        form_initials = self._get_customer_form_initials()
        form = CustomerInformationForm(
            self.request.POST or None,
            initial=form_initials
        )
        return form

    def _get_customer_form_initials(self) -> CustomerFormInitials:
        primary_shipping_address = self._get_customer_primary_address()
        initials = {
            'first_name': self.customer.first_name or '',
            'last_name': self.customer.last_name or '',
            'phone': self.customer.phone or '',
            'address': primary_shipping_address.address or '',
            'city': primary_shipping_address.city or '',
            'state': primary_shipping_address.state or '',
            'zipcode': primary_shipping_address.zipcode or '',
        }
        return initials

    def _get_customer_primary_address(self) -> ShippingAddress:
        try:
            primary_shipping_address = ShippingAddress.objects.get(
                customer=self.customer,
                is_primary=True,
            )
        except Exception:
            raise NotImplementedError

        return primary_shipping_address

    def _clean_non_valid_addresses(self) -> None:
        non_valid_addresses = ShippingAddress.objects.filter(
            customer=self.customer,
            is_primary=False,
            address_isnull=True
        ).delete()


# ==============================================================================

def is_all_cart_products_in_stock(
    ordered_products: list[OrderedProduct]
) -> bool:
    """
    This function checks if in stock are still
    enough products to process the order.
    It's made for a situations when one customer is filling the card
    and at the same time another customer bought all the cables first one need
    """
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        if cable.units_in_stock < ordered_product.quantity:
            return False

    return True


def update_cables_quantity_in_stock(
    ordered_products: list[OrderedProduct]
) -> None:
    """This function updates in stock quantity of ordered cables"""
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        cable.units_in_stock = F('units_in_stock') - ordered_product.quantity
        cable.save()


def correct_cart_products_quantity(
    ordered_products: list[OrderedProduct]
) -> None:
    for ordered_product in ordered_products:
        cable: Cable = Cable.objects.get(pk=ordered_product.product.pk)
        if ordered_product.quantity > cable.units_in_stock:
            ordered_product.quantity = cable.units_in_stock
            ordered_product.save()
