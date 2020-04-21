
from django import forms
from account.models.users import User

from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger("app")

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

    def is_duplicate_email(self):
        email = self.data['email']
        users = User.objects.filter(email=email)
        if len(users) > 0:
            logger.info(f'Validation fail duplicate email: {email}')
            raise ValidationError('10〜100歳が範囲ですよ!')
            return True
        return False


class SignUpForm(forms.Form):

    def check_email(email):
        users = User.objects.filter(email=email)
        if len(users) > 0:
            logger.info(f'Validation fail duplicate email: {email}')
            raise ValidationError('既に登録済みのメールアドレスです。')

    email = forms.CharField(
        label='Email',
        max_length=128,
        required=True,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email'}
        ),
        validators=[check_email]
    )
    password = forms.CharField(
        label='Password',
        max_length=128,
        required=True,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'}
        )
    )
