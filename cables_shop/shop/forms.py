from typing import TypedDict

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from shop.models import Customer


class CheckoutFormInitials(TypedDict):
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    zipcode: str


class UserRegistrationForm(UserCreationForm):
    """User registration form"""

    # Changing styles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'email', 'password1', 'password2'):
            self.fields[field].widget.attrs.update(
                {
                    'type': 'text',
                    'class': "form-control",
                }
            )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class CheckoutForm(forms.Form):
    """
    Form for checkout page.
    Handling both customer and shipping address models
    """
    first_name = forms.CharField(
        label='Имя',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иван'
                }
            )
        )
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иванов'
                }
            )
        )
    )
    phone = forms.CharField(
        label='Номер телефона',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+7 987 654-32-10'
                }
            )
        )
    )
    address = forms.CharField(
        label='Адрес',
        max_length=200,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Улица Пушкина, д. 10, кв. 55'
                }
            )
        )
    )
    city = forms.CharField(
        label='Город',
        max_length=50,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Санкт-Петербург'
                }
            )
        )
    )
    state = forms.CharField(
        label='Область',
        max_length=70,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ленинградская обл.'
                }
            )
        )
    )
    zipcode = forms.CharField(
        label='Почтовый индекс',
        max_length=10,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '195267'
                }
            )
        )
    )

    @staticmethod
    def get_checkout_form_initials(customer: Customer) -> CheckoutFormInitials:
        last_address = customer.shippingaddress_set.last()

        initials = {
            'first_name': customer.first_name or '',
            'last_name': customer.last_name or '',
            'phone': customer.phone or '',
            'address': last_address.address if last_address else '',
            'city': last_address.city if last_address else '',
            'state': last_address.state if last_address else '',
            'zipcode': last_address.zipcode if last_address else '',
        }
        return initials
