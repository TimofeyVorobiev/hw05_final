from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TextInput
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

        widgets = {
            'first_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': '30',
                    'placeholder': 'Имя'}),
            'last_name': TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': '150',
                    'placeholder': 'Фамилия'}),
            'username': TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': '150',
                    'placeholder': 'Имя пользователя'}),
            'email': TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': '254',
                    'placeholder': 'Адрес электронной почты'}),
        }
