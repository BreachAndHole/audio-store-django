from django.test import TestCase
from django.urls import reverse, resolve
from shop.models import Order, Cable, CableType, User
from shop import views


class URLsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.ru',
            first_name='Sergey',
            last_name='Frolov',
            phone_number='+79261234567',
            password='test_password',
        )

        self.accepted_order = Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.ACCEPTED,
            delivery_type=Order.DeliveryType.PICK_UP,
        )
        self.in_cart_order = Order.objects.create(
            customer=self.user,
            status=Order.OrderStatus.IN_CART,
            delivery_type=Order.DeliveryType.DELIVERY,
        )

    def test_home_page_access(self):
        url = reverse('home_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.IndexPageView)
        self.assertEqual(response.status_code, 200)

    def test_all_cables_page_access(self):
        url = reverse('all_cables_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.AllCablesPageView)
        self.assertEqual(response.status_code, 200)

    def test_cable_page_access(self):
        cable_type = CableType.objects.create(
            name='test type',
            name_plural='test type cables',
            description='description',
        )
        cable = Cable.objects.create(
            name='test cable',
            slug='test-cable',
            length_sm=100,
            price=100,
            units_in_stock=10,
            description='description',
            is_for_sale=True,
            type=cable_type,
        )
        url = reverse('cable_page', kwargs={'cable_slug': cable.slug})
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.CablePageView)
        self.assertEqual(response.status_code, 200)

    def test_user_registration_page_access(self):
        url = reverse('user_registration_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.UserRegistrationView)
        self.assertEqual(response.status_code, 200)

    def test_user_login_page_access(self):
        url = reverse('user_login_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func, views.user_login)
        self.assertEqual(response.status_code, 200)

    def test_user_logout_page_redirect(self):
        url = reverse('user_logout_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.UserLogoutView)
        self.assertEqual(response.status_code, 302)

    def test_user_logout_page_access(self):
        url = reverse('user_logout_page')
        self.client.login(username=self.user.email, password=self.user.password)
        response = self.client.get(url, follow=True)

        self.assertEqual(resolve(url).func.view_class, views.UserLogoutView)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_page_redirect(self):
        url = reverse('user_profile_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.UserProfileView)
        self.assertEqual(response.status_code, 302)

    def test_user_profile_page_access(self):
        url = reverse('user_profile_page')
        self.client.login(username=self.user.email, password=self.user.password)
        response = self.client.get(url, follow=True)
        self.assertEqual(resolve(url).func.view_class, views.UserProfileView)
        self.assertEqual(response.status_code, 200)

    def test_cart_page_redirect(self):
        url = reverse('cart_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.CartPageView)
        self.assertEqual(response.status_code, 302)

    def test_cart_page_access(self):
        url = reverse('cart_page')
        self.client.login(username=self.user.email, password=self.user.password)
        response = self.client.get(url, follow=True)

        self.assertEqual(resolve(url).func.view_class, views.CartPageView)
        self.assertEqual(response.status_code, 200)

    def test_checkout_page_redirect(self):
        url = reverse('checkout_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func, views.checkout)
        self.assertEqual(response.status_code, 302)

    def test_checkout_page_access(self):
        url = reverse('checkout_page')
        self.client.login(username=self.user.email, password=self.user.password)
        response = self.client.get(url, follow=True)

        self.assertEqual(resolve(url).func, views.checkout)
        self.assertEqual(response.status_code, 200)

    def test_update_cart_page_redirect(self):
        url = reverse('update_cart_page')
        response = self.client.get(url)

        self.assertEqual(resolve(url).func, views.update_cart)
        self.assertEqual(response.status_code, 302)

    def test_order_info_page_redirect(self):
        """
        If user is not logged in, he must be redirected to login page
        """
        url = reverse('order_info_page', kwargs={'order_pk': self.accepted_order.pk})
        response = self.client.get(url)

        self.assertEqual(resolve(url).func.view_class, views.OrderView)
        self.assertEqual(response.status_code, 302)

    def test_order_info_page_access(self):
        """
        If user is logged in, he must be able to see his order info page
        """
        url = reverse('order_info_page', kwargs={'order_pk': self.accepted_order.pk})
        self.client.login(username=self.user.email, password=self.user.password)
        response = self.client.get(url, follow=True)
        self.assertEqual(resolve(url).func.view_class, views.OrderView)
        self.assertEqual(response.status_code, 200)

    def test_not_this_user_order_info_page_redirect(self):
        """
        If user is trying to access order info page of another user,
        he must be redirected to home page.
        """
        url = reverse('order_info_page', kwargs={'order_pk': self.accepted_order.pk})
        user_2 = User.objects.create_user(
            email='test2@test.ru',
            first_name='Vasiliy',
            last_name='Petrov',
            phone_number='+79261234564',
            password='test_password2',
        )
        self.client.login(username=user_2.email, password=user_2.password)
        response = self.client.get(url)
        self.assertEqual(resolve(url).func.view_class, views.OrderView)
        self.assertEqual(response.status_code, 302)

    def test_not_accepted_order_info_page_redirect(self):
        """
        If order is not checked out,
        user must be redirected to home page
        """
        url = reverse('order_info_page', kwargs={'order_pk': self.in_cart_order.pk})
        self.client.login(
            username=self.user.email,
            password=self.user.password
        )
        response = self.client.get(url)
        self.assertEqual(resolve(url).func.view_class, views.OrderView)
        self.assertEqual(response.status_code, 302)
