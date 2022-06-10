from django.contrib import auth
from django.test import TestCase, Client
from django.urls import reverse
from shop.models import Order, Cable, CableType, ShippingAddress, User


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            'test@test.ru',
            'Sergey',
            'Frolov',
            '+79261234567',
            'test_password',
        )
        self.order = Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.ACCEPTED,
            delivery_type=Order.DeliveryType.PICK_UP,
        )
        Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.IN_CART,
            delivery_type=Order.DeliveryType.DELIVERY,
        )

        # URLs
        self.index_url = reverse('home_page')
        self.all_cables_url = reverse('all_cables_page')
        self.cart_url = reverse('cart_page')
        self.registration_url = reverse('user_registration_page')
        self.login_url = reverse('user_login_page')
        self.user_profile_url = reverse('user_profile_page')
        self.order_url = reverse('order_info_page', kwargs={'order_pk': self.order.pk})
        self.logout_url = reverse('user_logout_page')
        self.about_url = reverse('about_page')
        self.profile_url = reverse('user_profile_page')


class SimpleViewsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.cable_type = CableType.objects.create(
            name='test type',
            name_plural='test type cables',
            slug='test-type',
            description='description',
        )
        self.cable = Cable.objects.create(
            name='test cable',
            slug='test-cable',
            length_sm=100,
            price=100,
            units_in_stock=10,
            description='description',
            is_for_sale=True,
            type=self.cable_type,
        )

        self.cable_url = reverse('cable_page', kwargs={'cable_slug': self.cable.slug})

    def test_home_page_GET(self):
        template_name = 'shop/index.html'
        title = 'Главная страница'
        response = self.client.get(self.index_url)

        cable_types = response.context['cable_types']
        page_title = response.context['title']
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(cable_types.count(), 1)
        self.assertEqual(page_title, title)

    def test_all_cables_page_GET(self):
        template_name = 'shop/all_cables.html'
        title = 'Товары'

        response = self.client.get(self.all_cables_url)
        cables = response.context['cables']
        page_title = response.context['title']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(cables.count(), 1)
        self.assertEqual(page_title, title)

    def test_cable_page_GET(self):
        template_name = 'shop/cable.html'
        title = f'Страница товара - {self.cable.name}'
        response = self.client.get(self.cable_url)

        cable = response.context['cable']
        page_title = response.context['title']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(cable, self.cable)
        self.assertEqual(page_title, title)


class AboutPageTestCase(BaseTestCase):

    def setUp(self):
        super(AboutPageTestCase, self).setUp()

    def test_about_page_GET(self):
        template_name = 'shop/about.html'
        title = 'Обо мне'
        response = self.client.get(reverse('about_page'))

        page_title = response.context['title']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(page_title, title)


class UserRegistrationTestCase(BaseTestCase):
    """ User registration related tests """

    def setUp(self):
        super().setUp()

    def test_user_registration_page_GET(self):
        template_name = 'shop/registration.html'
        response = self.client.get(self.registration_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

    def test_user_registration_valid_POST(self):
        """
        If the form is valid, user must be created and redirected to the login page
        """
        form_post_data = {
            'email': 'lemur@mail.ru',
            'last_name': 'Сергей',
            'first_name': 'Фролов',
            'phone_number': '+79119234723',
            'password1': 'Sergey_11',
            'password2': 'Sergey_11'
        }
        response = self.client.post(self.registration_url, form_post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='lemur@mail.ru').count(), 1)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_user_registration_invalid_email_POST(self):
        form_post_data = {
            'email': 'lemur@mailru',
            'last_name': 'Сергей',
            'first_name': 'Фролов',
            'phone_number': '+79119234723',
            'password1': 'Sergey_11',
            'password2': 'Sergey_11'
        }
        response = self.client.post(self.registration_url, form_post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='lemur@mail.ru').count(), 0)
        self.assertTemplateUsed(response, 'shop/registration.html')

    def test_user_registration_invalid_phone_POST(self):
        form_post_data = {
            'email': 'lemur@mail.ru',
            'last_name': 'Сергей',
            'first_name': 'Фролов',
            'phone_number': '+791f9234723',
            'password1': 'Sergey_11',
            'password2': 'Sergey_11'
        }
        response = self.client.post(self.registration_url, form_post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='lemur@mail.ru').count(), 0)
        self.assertTemplateUsed(response, 'shop/registration.html')

    def test_user_registration_invalid_password_POST(self):
        form_post_data = {
            'email': 'lemur@mail.ru',
            'last_name': 'Сергей',
            'first_name': 'Фролов',
            'phone_number': '+79119234723',
            'password1': 'Sergey_1',
            'password2': 'Sergey_11'
        }
        response = self.client.post(self.registration_url, form_post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='lemur@mail.ru').count(), 0)
        self.assertTemplateUsed(response, 'shop/registration.html')


class UserLoginLogoutTestCase(BaseTestCase):
    """ User login related tests """

    def setUp(self):
        super().setUp()

    def test_user_login_page_can_access(self):
        template_name = 'shop/login.html'
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

    def test_user_logout_page_GET(self):
        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)


class UserProfilePageTestCase(BaseTestCase):
    """ User profile related tests """

    def setUp(self):
        super().setUp()

    def test_user_profile_page_can_access(self):
        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.profile_url)
        self.assertTemplateUsed(response, 'shop/user_profile.html')
        self.assertEqual(response.status_code, 200)

    def test_orders_display_correctly(self):
        """ IN_CART orders shouldn't be displayed in user profile"""
        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.profile_url)
        orders_on_page = response.context['orders']

        self.assertEqual(Order.objects.filter(customer=self.user).count(), 2)
        self.assertEqual(orders_on_page.count(), 1)

    def test_no_shipping_address_is_none_display_correctly(self):
        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.profile_url)
        shipping_address = response.context['last_used_address']

        self.assertIsNone(shipping_address)

    def test_no_shipping_address_exists_display_correctly(self):
        shipping_address = ShippingAddress.objects.create(
            customer=self.user,
            address='test address',
            city='test city',
            state='test state',
            zipcode='1244',
        )

        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.profile_url)
        displayed_shipping_address = response.context['last_used_address']

        self.assertEqual(displayed_shipping_address, shipping_address)


class OrderPageTestCase(BaseTestCase):
    """ Order related tests """

    def setUp(self):
        super().setUp()

    def test_accepted_delivery_order(self):
        self.client.force_login(self.user)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_info.html')
        self.assertEqual(response.context['order'], self.order)

    def test_not_this_user_order_redirect(self):
        """
        If user tries to access order page of another user,
        he should be redirected to his profile page
        """
        user2 = User.objects.create_user(
            'test2@mail.ru',
            'Sergey',
            'Frolov',
            '+79261234367',
            'test_password2',
        )
        self.client.force_login(user2)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

        # Test if user got redirected
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, 302)

        # Test if user got redirected to profile page
        response = self.client.get(self.order_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/user_profile.html')
