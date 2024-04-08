from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import ResetForm, SignUpForm


class SignUpView(CreateView):
    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('reviews:index')


class ResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    form_class = ResetForm
    success_url = reverse_lazy('users:password_reset_done')
