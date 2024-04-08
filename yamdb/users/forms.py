from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class ResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        email_exists = User.objects.filter(email=email)
        if not email_exists:
            self.add_error('email', 'Такой email не надйен.')
        return email
