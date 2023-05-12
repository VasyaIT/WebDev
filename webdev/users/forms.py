from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, \
    SetPasswordForm

User = get_user_model()


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password confirm'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LogInForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"placeholder": 'Username', 'autofocus': True}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True, 'placeholder': 'Old password'}
        ),
    )
    new_password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder': 'New password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder': 'Confirm password'}),
    )
