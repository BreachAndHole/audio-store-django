from django.test import TestCase

from shop import config
from shop.models import (Cable, CablePhoto, CableType, Order, OrderedProduct,
                         ShippingAddress, User)


class BaseTestCase(TestCase):

    def setUp(self):
        self.cable_type_with_photo = CableType.objects.create(
            name='test type',
            name_plural='test type cables',
            description='description',
            photo='cable_type_photo.jpg',
        )
        self.cable_type_without_photo = CableType.objects.create(
            name='test type 2',
            name_plural='test type cables 2',
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
            email='test@test.ru',
            first_name='Sergey',
            last_name='Frolov',
            phone_number='+79261234567',
            password='test_password',
        )


class CablesTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_cable_type_str(self):
        self.assertEqual(str(self.cable_type_with_photo), 'test type')

    def test_cable_type_photo_url(self):
        self.assertEqual(
            self.cable_type_with_photo.photo_url,
            '/media/cable_type_photo.jpg'
        )
        self.assertEqual(self.cable_type_without_photo.photo_url, '')

    def test_cable_str(self):
        self.assertEqual(str(self.cable_with_photo), 'test cable, 100 ????.')

    def test_cable_absolute_url(self):
        self.assertEqual(self.cable_with_photo.get_absolute_url(), '/cable/test-cable')

    def test_cable_title_photo_url(self):
        self.assertEqual(
            self.cable_with_photo.title_photo_url,
            '/media/test_title_photo.jpg'
        )
        self.assertEqual(self.cable_without_photo.title_photo_url, '')

    def test_cable_photo_str(self):
        self.assertEqual(str(self.title_cable_photo), 'title test ...')
        self.assertEqual(str(self.nontitle_cable_photo), 'test ...')


class UserTestCase(BaseTestCase):
    """
    This test case covering custom User model and CustomUserManager functionality
    """

    def setUp(self):
        super().setUp()

    def test_customer_str(self):
        self.assertEqual(str(self.user), 'test@test.ru')

    def test_user_manager_no_email_error(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            '',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
        )

    def test_user_manager_no_password_error(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            'test@mail.ru',
            '',
            'Sergey',
            'Frolov',
            '+79219084376',
        )

    def test_user_manager_no_phone_error(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '',
        )

    def test_create_superuser_valid(self):
        user = User.objects.create_superuser(
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_not_staff_error(self):
        self.assertRaises(
            ValueError,
            User.objects.create_superuser,
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
            is_staff=False,
        )

    def test_create_superuser_not_superuser_error(self):
        self.assertRaises(
            ValueError,
            User.objects.create_superuser,
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
            is_superuser=False,
        )


class OrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.shipping_address = ShippingAddress.objects.create(
            customer=self.user,
            address='test address',
            city='test city',
            state='test state',
            zipcode='1234',
        )
        self.order_in_cart = Order.objects.create(
            customer=self.user,
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
            customer=self.user,
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
            '?????????? ???????????????????? test@test.ru, 1234'
        )

    def test_ordered_product_str(self):
        self.assertEqual(str(self.product_1_in_cart), '#9, test cable, 100 ????.')

    def test_get_product_total_price(self):
        self.assertEqual(self.product_1_in_cart.total_price, 300)

    def test_order_str(self):
        self.assertEqual(str(self.order_in_cart), '???5: test@test.ru, ?? ??????????????')

    def test_order_absolute_url(self):
        self.assertEqual(self.order_in_cart.get_absolute_url(), '/order/3')

    def test_products_total_price(self):
        self.assertEqual(self.order_in_cart.products_total_price, 900)

    def test_order_total_price(self):
        self.assertEqual(
            self.order_in_cart.order_total_price,
            900 + config.DELIVERY_PRICE
        )
        self.assertEqual(self.accepted_order_pick_up.order_total_price, 500)
