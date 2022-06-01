from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    """User registration form"""

    # Changing styles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'email', 'password1', 'password2'):
            self.fields[field].widget.attrs.update({
                'type': 'text',
                'class': "form-control",
            })

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class CustomerInformationForm(forms.Form):
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
