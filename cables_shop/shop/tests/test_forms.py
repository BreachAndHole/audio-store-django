from django.test import TestCase

from shop.forms import UserInformationForm
from shop.models import ShippingAddress, User


class UserInformationFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test@mail.ru',
            'test_password',
            'Sergey',
            'Frolov',
            '+79219084376',
        )

    def test_get_form_initials_without_address(self):
        self.assertEqual(
            UserInformationForm.get_user_information_form_initials(self.user),
            {
                'first_name': 'Sergey',
                'last_name': 'Frolov',
                'phone_number': '+79219084376',
                'address': '',
                'city': '',
                'state': '',
                'zipcode': '',
            }
        )

    def test_get_form_initials_with_address(self):
        ShippingAddress.objects.create(
            customer=self.user,
            address='test address',
            city='test city',
            state='test state',
            zipcode='1234',
        )
        self.assertEqual(
            UserInformationForm.get_user_information_form_initials(self.user),
            {
                'first_name': 'Sergey',
                'last_name': 'Frolov',
                'phone_number': '+79219084376',
                'address': 'test address',
                'city': 'test city',
                'state': 'test state',
                'zipcode': '1234',
            }
        )
