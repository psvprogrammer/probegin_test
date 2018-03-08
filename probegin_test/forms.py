from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form which uses bootstrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'login or email'}))
    password = forms.CharField(label='Your password',
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'password'}))
