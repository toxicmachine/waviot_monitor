from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _


from .models import User


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control text-center mb-2',}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control text-center',}))
    error_messages = {
        "invalid_login": _(
            "Неверный логин или пароль!"
        ),
    }

    class Meta:
        model = User
        fields = ['username', 'password']


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль",
                                   widget=forms.PasswordInput(attrs={'class': 'form-control text-center mb-2'}))
    new_password1 = forms.CharField(label="Новый пароль",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control text-center mb-2'}))
    new_password2 = forms.CharField(label="Подтверждение пароля",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control text-center'}))

    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Ваш старый пароль введен неправильно. Повторите попытку."
        ),
        "password_mismatch": _("Введенные пароли не совпадают."),
    }

    def __init__(self, *args, **kwargs):
        self.user = User
        super().__init__(*args, **kwargs)

