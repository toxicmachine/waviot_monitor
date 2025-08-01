from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import render
from django.urls import resolve, reverse_lazy
from django.views.generic import TemplateView

from .forms import LoginUserForm, UserPasswordChangeForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = '/data-overview'
    extra_context = {
        'title': 'Мониторинг работы УСПД',
        'header': 'Мониторинг работы УСПД',
    }


class ProfileUser(LoginRequiredMixin, TemplateView):
    form_class = LoginUserForm
    template_name = 'users/profile.html'
    extra_context = {
        'title': 'Мониторинг работы УСПД',
        'header': 'Мониторинг работы УСПД',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name

        return context


class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
    extra_context = {'title': "Изменение пароля",
                     'header': 'Мониторинг работы УСПД', }


class UserPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "users/password_reset_complete.html"
    title = 'Пароль успешно изменен!'

