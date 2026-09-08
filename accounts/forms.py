"""
Custom forms for authentication
"""
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm


class EmailAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that uses email field instead of username
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class ForcedPasswordChangeForm(SetPasswordForm):
    """
    Set a new password without asking for the old one.

    Used for the first-login password change: the account was created by an
    admin, so the user only knows a temporary password they are replacing.
    """
    new_password1 = forms.CharField(
        label='New password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a new password',
            'autocomplete': 'new-password',
            'autofocus': True,
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the same password again',
            'autocomplete': 'new-password',
        }),
    )
