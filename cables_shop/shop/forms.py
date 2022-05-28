from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Changing styles
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
