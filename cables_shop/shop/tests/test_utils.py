from django.test import TestCase
from shop.models import Order, ShippingAddress, User, OrderedProduct, Cable, CableType
from shop import utils


class UtilsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
        )
        self.cable_type = CableType.objects.create(
            name='test_cable_type',
            name_plural='test_cable_types',
            description='test_description',
            photo='test_cable_type_photo.jpg',
        )
        self.cable = Cable.objects.create(
            name='test_cable',
            slug='test_cable',
            length_sm=100,
            price=100,
            units_in_stock=10,
            description='test_description',
            type=self.cable_type,
        )

    def test_last_used_address_exist(self):
        shipping_address = ShippingAddress.objects.create(
            customer=self.user,
            address='test address',
            city='test city',
            state='test state',
            zipcode='1234',
        )
        self.assertEqual(
            utils.get_last_used_customer_address(self.user),
            shipping_address
        )

    def test_last_used_address_not_exist(self):
        self.assertIsNone(utils.get_last_used_customer_address(self.user))

    def test_create_empty_cart_not_existed(self):
        utils.create_empty_cart(self.user)
        self.assertEqual(Order.objects.filter(customer=self.user).count(), 1)

    def test_create_empty_cart_existed(self):
        Order.objects.create(customer=self.user, status=Order.OrderStatus.IN_CART)

        utils.create_empty_cart(self.user)
        self.assertEqual(Order.objects.filter(customer=self.user).count(), 1)

    def test_create_empty_cart_existed_with_other_orders(self):
        Order.objects.create(customer=self.user, status=Order.OrderStatus.ACCEPTED)
        Order.objects.create(customer=self.user, status=Order.OrderStatus.IN_CART)

        utils.create_empty_cart(self.user)
        self.assertEqual(
            Order.objects.filter(
                customer=self.user,
                status=Order.OrderStatus.IN_CART
            ).count(),
            1
        )
        self.assertEqual(
            Order.objects.filter(
                customer=self.user,
                status=Order.OrderStatus.ACCEPTED
            ).count(),
            1
        )

    def test_save_ordered_product(self):
        order = Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.IN_CART
        )
        ordered_product = OrderedProduct.objects.create(
            order=order,
            product=self.cable,
            quantity=2,
        )
        utils.save_or_delete_ordered_product(ordered_product)
        self.assertEqual(OrderedProduct.objects.count(), 1)
        self.assertEqual(ordered_product.quantity, 2)

    def test_delete_ordered_product(self):
        order = Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.IN_CART
        )
        ordered_product = OrderedProduct.objects.create(
            order=order,
            product=self.cable,
            quantity=-1,
        )
        self.assertEqual(OrderedProduct.objects.count(), 1)
        utils.save_or_delete_ordered_product(ordered_product)
        self.assertEqual(OrderedProduct.objects.count(), 0)
