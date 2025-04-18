from django import forms
from django.contrib.auth.forms import PasswordResetForm

class StyledPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'custom-input',
            'placeholder': 'Enter your email'
        }),
        label="Email Address"
    )

