import re

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import EmailField

from users.models import EmailPatternWhitelist, ContentUpdateRequest

UserModel = get_user_model()

from django import forms

from people.models import Person


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        self.has_invite = kwargs.pop('has_invite', False)
        super().__init__(*args, **kwargs)
        if self.has_invite:
            self.fields.pop('email')
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_password(self):
        pw = self.cleaned_data['password']
        validate_password(pw)
        return pw

    def clean(self):
        if not self.has_invite and self.cleaned_data.get('email'):
            email = self.cleaned_data.get('email')
            if not any(
                    [re.compile(whitelist.pattern).match(email) for whitelist in EmailPatternWhitelist.objects.all()]):
                self.add_error('email', 'The email pattern is invalid')

            if UserModel.objects.filter(email=email).exists():
                self.add_error('email', 'User with this email already exists')

        if self.cleaned_data.get('username') and UserModel.objects.filter(
                username=self.cleaned_data['username']).exists():
            self.add_error('username', 'User with this username already exists')

        if self.cleaned_data.get('password_confirm') and self.cleaned_data.get('password') != self.cleaned_data.get(
                'password_confirm'):
            self.add_error('password_confirm', 'Passwords don\'t match')

        return self.cleaned_data

    class Meta:
        model = UserModel
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name',)


class LoginOverrideForm(forms.Form):
    login_as = forms.ModelChoiceField(queryset=Person.qs.order_by('-is_superuser', '-is_staff', 'last_name'))


class PasswordResetRequestForm(forms.Form):
    email = EmailField()
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(
        attrs={
            'data-theme': 'dark',
        }
    ))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email.split('@')[-1] == 'trojsten.sk':
            raise ValidationError('You can login using Trojsten Google OAuth')

        try:
            person = Person.objects.get(email=email)
            self.cleaned_data['person'] = person
        except Person.DoesNotExist:
            raise ValidationError("No user with this email exists")
        return email


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        pw = self.cleaned_data['new_password']
        validate_password(pw, self.user)
        return pw

    def clean(self):
        if 'new_password' in self.cleaned_data and self.cleaned_data['new_password'] != self.cleaned_data[
            'confirm_password']:
            raise ValidationError('The passwords do not match')

        return self.cleaned_data

    class Meta:
        fields = ('new_password', 'confirm_password')


class ContentUpdateRequestForm(forms.ModelForm):
    class Meta:
        model = ContentUpdateRequest
        fields = ('content',)
