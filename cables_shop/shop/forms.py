from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    # Changing styles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'email', 'password1', 'password2'):
            self.fields[field].widget.attrs.update({
                'type': 'text',
                'id': 'form3Example1c',
                'class': "form-control",
            })

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        label='Имя',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иван',
                }
            )
        ),
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иванов',
                }
            )
        ),
    )
    phone = forms.CharField(
        label='Номер телефона',
        max_length=15,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+7 999-111-22-33',
                }
            )
        ),
    )

    address = forms.CharField(
        label='Адрес',
        max_length=200,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Московский проспект 322, кв. 69',
                }
            )
        ),
    )
    city = forms.CharField(
        label='Город',
        max_length=50,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Санкт-Петербург',
                }
            )
        ),
    )
    state = forms.CharField(
        label='Область',
        max_length=70,
        required=False,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ленинградская область',
                }
            )
        ),
    )
    zipcode = forms.CharField(
        label='Почтовый индекс',
        max_length=10,
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '123456',
                }
            )
        ),
    )