from django import forms
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field import formfields

from shop import utils
from shop.models import User


class UserRegistrationForm(UserCreationForm):
    """ Overrider User registration form """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Changing fields style
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update(
                {'type': 'text', 'class': "form-control"}
            )
        # Adding placeholders
        self.fields['email'].widget.attrs.update({'placeholder': 'Ivan@mail.com'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Иван'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Иванов'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': '+7 (911) 987-65-43'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Password'})

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password1',
            'password2',
        )

        error_messages = {
            'email': {
                'required': 'Необходимо ввести Email',
                'invalid': 'Email введён неверно',
                'unique': 'Пользователь с таким Email уже зарегистрирован'
            },
            'phone_number': {
                'required': 'Необходимо ввести номер телефона',
                'invalid': 'Неверный формат номера телефона',
                'unique': 'Пользователь с таким номером телефона уже зарегистрирован'
            },
        }

    def clean_first_name(self, *args, **kwargs):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('Необходимо ввести имя')
        return first_name.title()

    def clean_last_name(self, *args, **kwargs):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('Необходимо ввести фамилию')
        return last_name.title()


class UserInformationForm(forms.Form):
    """
    Form for processing User information. used on checkout page as well as in profile
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
    phone_number = formfields.PhoneNumberField(
        label='Номер телефона',
        widget=(
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+7 (980) 765-43-21'
                }
            )
        )
    )
    address = forms.CharField(
        label='Адрес',
        max_length=200,
        required=False,
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
        required=False,
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
        required=False,
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
        required=False,
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
    def get_user_information_form_initials(customer: User) -> dict:
        last_address = utils.get_last_used_customer_address(customer)

        initials = {
            'first_name': customer.first_name or '',
            'last_name': customer.last_name or '',
            'phone_number': customer.phone_number or '',
            'address': last_address.address if last_address else '',
            'city': last_address.city if last_address else '',
            'state': last_address.state if last_address else '',
            'zipcode': last_address.zipcode if last_address else '',
        }
        return initials
