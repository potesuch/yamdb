from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import ResetForm, SignUpForm


class SignUpView(CreateView):
    """
    Представление для регистрации нового пользователя.

    Отображает форму SignUpForm для ввода данных пользователя.
    После успешной регистрации перенаправляет пользователя на указанную страницу.
    """
    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('reviews:index')


class ResetView(PasswordResetView):
    """
    Представление для сброса пароля.

    Отображает форму ResetForm для ввода электронной почты пользователя.
    Проверяет наличие введенной электронной почты в базе данных перед отправкой письма с инструкциями по сбросу пароля.
    """
    template_name = 'users/password_reset.html'
    form_class = ResetForm
    success_url = reverse_lazy('users:password_reset_done')
