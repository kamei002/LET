
from django import forms


class LoginForm(forms.Form):
      
    email = forms.CharField(
        label='Email',
        max_length=128,
        required=True,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email'}
        )
    )
    password = forms.CharField(
        label='Password',
        max_length=128,
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'}
        )
    )
