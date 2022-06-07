from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from shop.views import *
from shop.models import *


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            username='login_test_user',
            email='loginTest@test.ru',
            password='Test_password',
        )
        order = Order.objects.create(
            customer=self.user.customer,
            status=Order.OrderStatus.ACCEPTED,
            delivery_type=Order.DeliveryType.PICK_UP,
        )

        # URLs
        self.index_url = reverse('home_page')
        self.all_cables_url = reverse('all_cables_page')
        self.cart_url = reverse('cart_page')
        self.registration_url = reverse('user_registration_page')
        self.login_url = reverse('user_login_page')
        self.user_profile_url = reverse('user_profile_page')
        self.order_url = reverse(
            'order_info_page', kwargs={'order_pk': order.pk}
        )
        self.logout_url = reverse('user_logout_page')


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
            type=self.cable_type,
        )

        self.cable_url = reverse(
            'cable_page',
            kwargs={'cable_slug': self.cable.slug}
        )

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


class UserRegistrationTestCase(BaseTestCase):
    """ User registration related tests """

    def setUp(self):
        super().setUp()

    def test_user_registration_page_GET(self):
        template_name = 'shop/registration.html'
        response = self.client.get(self.registration_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

    def test_user_registration_page_valid_POST(self):
        """
        If the form is valid, user must be created and redirected to the
        home page
        """
        registration_form_post_data = {
            'username': 'testuser2',
            'email': 'test2@mail.ru',
            'password1': 'Frolov_35',
            'password2': 'Frolov_35',
        }
        response = self.client.post(
            self.registration_url,
            registration_form_post_data,
        )
        [print(t.name) for t in response.templates]
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            User.objects.filter(username='testuser2').count(),
            1
        )

    def test_user_registration_page_invalid_POST(self):
        """
        If the form is invalid, user must not be created
        and stay on the same page
        """
        registration_form_post_data = {
            'username': 'testuser2',
            'email': 'test2@mail.ru',
            'password1': 'Frolov',
            'password2': 'Frolov_35',
        }
        response = self.client.post(
            self.registration_url,
            registration_form_post_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.filter(username='testuser2').count(),
            0
        )


class UserLoginLogoutTestCase(BaseTestCase):
    """ User login related tests """

    def setUp(self):
        super().setUp()

    def test_user_login_page_GET(self):
        template_name = 'shop/login.html'
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

    def test_user_logout_page_GET(self):
        self.client.login(
            username=self.user.username,
            password=self.user.password
        )
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 302)

    # ODO: test login POST valid
    # ODO: test login POST invalid


class UserProfilePageTestCase(BaseTestCase):
    """ User profile related tests """

    def setUp(self):
        super().setUp()

    # ODO: test profile page GET

    # ODO: test order info GET


class OrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    # ODO: test cart page GET

    # ODO: test checkout page GET
    # ODO: test checkout page POST valid
    # ODO: test checkout page POST invalid

    # ODO: test update_cart json parse error
    # ODO: test update_cart update error
