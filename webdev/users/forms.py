from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth import forms as form
from django.core.exceptions import ValidationError

User = get_user_model()


class SignUpForm(form.UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password confirm'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use')
        return email

    def clean_username(self):
        """Reject usernames that differ only in case."""
        username = self.cleaned_data.get("username")
        if (
            username
            and self._meta.model.objects.filter(username__iexact=username).exists()
            and self._meta.model.objects.filter(email__iexact=username).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "username": self.instance.unique_error_message(
                            self._meta.model, ["username"]
                        )
                    }
                )
            )
        else:
            return username


class LogInForm(form.AuthenticationForm):
    username = form.UsernameField(widget=forms.TextInput(attrs={"placeholder": 'Username or email', 'autofocus': True}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class CustomPasswordChangeForm(form.PasswordChangeForm):
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


class CustomPasswordResetForm(form.PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", 'placeholder': 'Email'}),
    )


class CustomSetPasswordForm(form.SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder': 'New password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder': 'New password confirmation'}),
    )
