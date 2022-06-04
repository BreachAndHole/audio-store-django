import json
from enum import Enum
from typing import NamedTuple, TypedDict
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from shop.errors import *
from shop.forms import CheckoutForm
from shop.models import *


class CartUpdateAction(Enum):
    ADD_TO_CART = 'add_to_cart'
    REMOVE_FROM_CART = 'remove_from_cart'
    DELETE_FROM_CART = 'delete_from_cart'


class CartUpdateParsedData(NamedTuple):
    product_id: int
    action: str


class CheckoutFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


class CartUpdateService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def process_cart_update(self) -> None:
        parsed_response = self.__parse_json_update_data()
        order, _ = Order.objects.get_or_create(
            customer=self.request.user.customer,
            status=Order.OrderStatus.IN_CART,
        )
        ordered_product = self.__get_product_to_update(
            order,
            parsed_response.product_id
        )
        self.__update_product_quantity_in_cart(
            ordered_product,
            parsed_response.action
        )
        self.__save_or_delete_product_in_cart(ordered_product)

    def __parse_json_update_data(self) -> CartUpdateParsedData:
        """
        This function is parsing json response from cart.js script.
        """
        try:
            received_data = json.loads(self.request.body)
        except json.JSONDecodeError:
            raise JSONResponseParsingError(
                'Error during json response decoding'
            )

        try:
            parsed_data = CartUpdateParsedData(
                product_id=received_data.get('productId'),
                action=received_data.get('action')
            )
        except KeyError:
            raise JSONResponseParsingError(
                'productId or action is not in response'
            )

        return parsed_data

    @staticmethod
    def __get_product_to_update(
            order: Order,
            product_id: int
    ) -> OrderedProduct:
        """Getting or creating new ordered product for further updating"""
        try:
            cable = Cable.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            raise CartUpdateError(
                f'There is no product with {product_id=}'
            )

        ordered_product, _ = OrderedProduct.objects.get_or_create(
            order=order,
            product=cable
        )
        return ordered_product

    @staticmethod
    def __update_product_quantity_in_cart(
            ordered_product: OrderedProduct,
            action: str
    ) -> None:
        """This function is changing quantity of product needed to update"""
        match action:
            case CartUpdateAction.ADD_TO_CART.value:
                units_in_stock = ordered_product.product.units_in_stock
                if ordered_product.quantity < units_in_stock:
                    ordered_product.quantity += 1
            case CartUpdateAction.REMOVE_FROM_CART.value:
                ordered_product.quantity -= 1
            case CartUpdateAction.DELETE_FROM_CART.value:
                ordered_product.quantity = 0
            case _:
                raise CartUpdateError(f'Undefined {action = }')

    @staticmethod
    def __save_or_delete_product_in_cart(
            ordered_product: OrderedProduct
    ) -> None:
        if ordered_product.quantity <= 0:
            ordered_product.delete()
        else:
            ordered_product.save()


class CheckoutService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.customer = self.request.user.customer
        self.order = Order.objects.get(
            customer=self.customer,
            status=Order.OrderStatus.IN_CART
        )
        self.ordered_products = self.order.orderedproduct_set.all()
        self.checkout_form = CheckoutForm(
            self.request.POST or None,
            initial=self.__get_checkout_form_initials()
        )

    def process_checkout(self) -> None:
        self.__update_customer_information()
        shipping_address = self.__get_shipping_address_for_this_order()

        if not self.__order_is_valid():
            raise ProductsQuantityError(
                'Ordered quantity is greater than available'
            )

        self.__update_products_in_stock()
        self.order.shipping_address = shipping_address
        self.order.status = Order.OrderStatus.ACCEPTED
        self.order.save()

    def __update_customer_information(self) -> None:
        checkout_form_data = self.checkout_form.cleaned_data
        self.customer.first_name = checkout_form_data.get('first_name', '')
        self.customer.last_name = checkout_form_data.get('last_name', '')
        self.customer.phone = checkout_form_data.get('phone', '')
        self.customer.save()

    def __get_shipping_address_for_this_order(self) -> ShippingAddress:
        checkout_form_data = self.checkout_form.cleaned_data
        try:
            shipping_address, _ = ShippingAddress.objects.get_or_create(
                customer=self.customer,
                address=checkout_form_data.get('address'),
                city=checkout_form_data.get('city'),
                state=checkout_form_data.get('state'),
                zipcode=checkout_form_data.get('zipcode'),
            )
        except KeyError:
            raise CreateShippingAddressError(
                'Error during shipping address creation'
            )
        return shipping_address

    def __order_is_valid(self) -> bool:
        for ordered_product in self.ordered_products:
            if ordered_product.quantity > ordered_product.product.units_in_stock:
                return False
        return True

    def __update_products_in_stock(self) -> None:
        for ordered_product in self.ordered_products:
            ordered_product.product.units_in_stock = max(
                0,
                ordered_product.product.units_in_stock - ordered_product.quantity
            )
            ordered_product.product.save()

    def correct_ordered_products(self) -> None:
        for ordered_product in self.ordered_products:
            ordered_product.quantity = ordered_product.product.units_in_stock
            ordered_product.save()

    def __get_checkout_form_initials(self) -> CheckoutFormInitials:

        last_address = self.customer.shippingaddress_set.last()

        initials = {
            'first_name': self.customer.first_name or '',
            'last_name': self.customer.last_name or '',
            'phone': self.customer.phone or '',
            'address': last_address.address if last_address else '',
            'city': last_address.city if last_address else '',
            'state': last_address.state if last_address else '',
            'zipcode': last_address.zipcode if last_address else '',
        }
        return initials
