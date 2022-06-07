from django.test import TestCase
from django.contrib.auth.models import User
from cables_shop.settings import DELIVERY_PRICE
from shop.models import *


class BaseTestCase(TestCase):

    def setUp(self):
        self.cable_type_with_photo = CableType.objects.create(
            name='test type',
            name_plural='test type cables',
            slug='test-type',
            description='description',
            photo='cable_type_photo.jpg',
        )
        self.cable_type_without_photo = CableType.objects.create(
            name='test type 2',
            name_plural='test type cables 2',
            slug='test-type-2',
            description='description 2',
        )

        self.cable_with_photo = Cable.objects.create(
            name='test cable',
            slug='test-cable',
            length_sm=100,
            price=100,
            units_in_stock=10,
            description='description',
            type=self.cable_type_with_photo,
        )
        self.cable_without_photo = Cable.objects.create(
            name='test cable 2',
            slug='test-cable-2',
            length_sm=50,
            price=150,
            units_in_stock=12,
            description='description 2',
            type=self.cable_type_without_photo,
        )

        self.title_cable_photo = CablePhoto.objects.create(
            photo='test_title_photo.jpg',
            cable=self.cable_with_photo,
            is_title=True,
        )
        self.nontitle_cable_photo = CablePhoto.objects.create(
            photo='test_nontitle_photo.jpg',
            cable=self.cable_with_photo,
            is_title=False,
        )
        self.user = User.objects.create_user(
            username='test_user',
            email='test@test.ru',
            password='Test_password',
        )
        self.customer = self.user.customer
        self.customer.first_name = 'Sergey'
        self.customer.last_name = 'Frolov'
        self.customer.phone = '+79998887766'
        self.customer.save()


class CablesTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_cable_type_str(self):
        self.assertEqual(
            str(self.cable_type_with_photo),
            'test type'
        )

    def test_cable_type_photo_url(self):
        self.assertEqual(
            self.cable_type_with_photo.photo_url,
            f'/media/cable_type_photo.jpg'
        )
        self.assertEqual(
            self.cable_type_without_photo.photo_url,
            ''
        )

    def test_cable_str(self):
        self.assertEqual(
            str(self.cable_with_photo),
            f'test cable, 100 см.'
        )

    def test_cable_absolute_url(self):
        self.assertEqual(
            self.cable_with_photo.get_absolute_url(),
            f'/cable/test-cable'
        )

    def test_cable_title_photo_url(self):
        self.assertEqual(
            self.cable_with_photo.title_photo_url,
            '/media/test_title_photo.jpg'
        )
        self.assertEqual(
            self.cable_without_photo.title_photo_url,
            ''
        )

    def test_cable_photo_str(self):
        self.assertEqual(
            str(self.title_cable_photo),
            f'title test ...'
        )
        self.assertEqual(
            str(self.nontitle_cable_photo),
            f'test ...'
        )


class CustomerTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_customer_str(self):
        self.assertEqual(
            str(self.customer),
            f'Frolov Sergey'
        )


class OrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.shipping_address = ShippingAddress.objects.create(
            customer=self.customer,
            address='test address',
            city='test city',
            state='test state',
            zipcode='1234',
        )
        self.order_in_cart = Order.objects.create(
            customer=self.customer,
            status=Order.OrderStatus.IN_CART,
            delivery_type=Order.DeliveryType.DELIVERY,
        )
        self.product_1_in_cart = OrderedProduct.objects.create(
            order=self.order_in_cart,
            product=self.cable_with_photo,
            quantity=3,
        )
        self.product_2_in_cart = OrderedProduct.objects.create(
            order=self.order_in_cart,
            product=self.cable_without_photo,
            quantity=4,
        )

        self.accepted_order_pick_up = Order.objects.create(
            customer=self.customer,
            status=Order.OrderStatus.ACCEPTED,
            delivery_type=Order.DeliveryType.PICK_UP,
        )
        self.product_3_accepted = OrderedProduct.objects.create(
            order=self.accepted_order_pick_up,
            product=self.cable_with_photo,
            quantity=5,
        )

    def test_shipping_address_str(self):
        self.assertEqual(
            str(self.shipping_address),
            f'Адрес покупателя Frolov Sergey, 1234'
        )

    def test_ordered_product_str(self):
        self.assertEqual(
            str(self.product_1_in_cart),
            f'#{self.product_1_in_cart.order.pk}, test cable, 100 см.'
        )

    def test_get_product_total_price(self):
        self.assertEqual(
            self.product_1_in_cart.product_total_price,
            300
        )

    def test_order_str(self):
        self.assertEqual(
            str(self.order_in_cart),
            f'№{self.order_in_cart.pk}: Frolov Sergey, В корзине'
        )

    def test_order_absolute_url(self):
        self.assertEqual(
            self.order_in_cart.get_absolute_url(),
            f'/user/order/{self.order_in_cart.pk}'
        )

    def test_products_total_price(self):
        self.assertEqual(
            self.order_in_cart.products_total_price,
            900
        )

    def test_order_total_price(self):
        self.assertEqual(
            self.order_in_cart.order_total_price,
            900 + DELIVERY_PRICE
        )
        self.assertEqual(
            self.accepted_order_pick_up.order_total_price,
            500
        )

    def test_order_total_products(self):
        self.assertEqual(
            self.order_in_cart.order_total_products,
            2
        )


class ReceiversTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    @staticmethod
    def assert_receiver_is_connected(receiver_string, signal, sender):
        receivers = signal._live_receivers(sender)
        receiver_strings = [f'{r.__module__}.{r.__name__}' for r in receivers]
        if receiver_string not in receiver_strings:
            raise AssertionError(
                '{} is not connected to signal.'.format(receiver_string)
            )

    def test_create_customer_profile(self):
        self.assert_receiver_is_connected(
            'shop.models.create_customer_profile',
            signal=post_save,
            sender=User,
        )

    def test_save_customer_profile(self):
        self.assert_receiver_is_connected(
            'shop.models.save_customer_profile',
            signal=post_save,
            sender=User,
        )
