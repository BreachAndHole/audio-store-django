import json
from enum import Enum
from typing import NamedTuple, Optional, TypedDict
from django.db import IntegrityError
from django.http import HttpRequest, QueryDict
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserInformationForm
from .models import Order, OrderedProduct, ShippingAddress, Cable, User

from . import utils

from .errors import *


class CartUpdateAction(Enum):
    ADD_TO_CART = 'add_to_cart'
    REMOVE_FROM_CART = 'remove_from_cart'
    DELETE_FROM_CART = 'delete_from_cart'


class CartUpdateParsedData(NamedTuple):
    product_id: int
    action: str


class CartUpdateService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def process_cart_update(self) -> None:
        parsed_response = self.__parse_json_update_data()
        order, _ = Order.objects.get_or_create(
            customer=self.request.user,
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
        utils.save_or_delete_ordered_product(ordered_product)

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
                product_id=int(received_data.get('productId')),
                action=received_data.get('action')
            )
        except KeyError:
            raise JSONResponseParsingError(
                'productId or action is not in response'
            )

        if parsed_data.product_id < 0:
            raise JSONResponseParsingError('Invalid product id')

        return parsed_data

    def __get_product_to_update(self, order: Order, product_id: int) -> OrderedProduct:
        """Getting or creating new ordered product for further updating"""
        try:
            cable = Cable.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            raise self.CartUpdateError(
                f'There is no product with {product_id=}'
            )

        ordered_product, _ = OrderedProduct.objects.get_or_create(
            order=order,
            product=cable
        )
        return ordered_product

    def __update_product_quantity_in_cart(
            self,
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
                raise self.CartUpdateError(f'Undefined {action = }')


class DeliveryTypeConverter(TypedDict):
    delivery: Order.DeliveryType
    selfPickUp: Order.DeliveryType


class UserInformationService:
    delivery_type_converter: DeliveryTypeConverter = {
        'delivery': Order.DeliveryType.DELIVERY,
        'selfPickUp': Order.DeliveryType.PICK_UP
    }

    def __init__(self, customer: User, post_request_data: Optional[QueryDict]) -> None:
        self.customer = customer
        self.order = Order.objects.get(
            customer=self.customer,
            status=Order.OrderStatus.IN_CART
        )
        self.ordered_products = OrderedProduct.objects.filter(
            order=self.order
        )
        self.form = UserInformationForm(
            post_request_data or None,
            initial=UserInformationForm.get_user_information_form_initials(
                self.customer
            )
        )
        self.delivery_type = self.delivery_type_converter.get(
            post_request_data.get('radioDeliveryType')
        )

    def process_checkout(self) -> None:
        self.__update_customer_information()

        if not self.__order_is_valid():
            raise ProductsQuantityError(
                'Ordered quantity is greater than available'
            )

        if self.delivery_type != Order.DeliveryType.PICK_UP:
            shipping_address = self.__get_shipping_address_from_form()

            # If delivery selected and address of city not entered
            if any([not shipping_address.address, not shipping_address.city]):
                raise ShippingAddressNotProvidedError
            self.order.shipping_address = shipping_address

        self.__update_products_in_stock()

        self.order.status = Order.OrderStatus.ACCEPTED
        self.order.delivery_type = self.delivery_type
        self.order.save()

    def process_information_update(self) -> None:
        self.__update_customer_information()
        shipping_address = self.__get_shipping_address_from_form()
        shipping_address.save()

    def __update_customer_information(self) -> None:
        checkout_form_data = self.form.cleaned_data
        self.customer.first_name = checkout_form_data.get('first_name')
        self.customer.last_name = checkout_form_data.get('last_name')

        # If user wants to change his phone number
        form_phone_number = checkout_form_data.get('phone_number')
        try:
            self.customer.phone_number = form_phone_number
            self.customer.save()
        except IntegrityError:
            raise PhoneNumberAlreadyExistsError(
                f'Phone number {form_phone_number} already attached to another user'
            )

    def __get_shipping_address_from_form(self) -> ShippingAddress:
        checkout_form_data = self.form.cleaned_data
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
