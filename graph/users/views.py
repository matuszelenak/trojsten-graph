from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView as Login
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView

from people.models import Person
from users.forms import LoginOverrideForm, LoginForm, PasswordResetRequestForm, PasswordResetForm, RegistrationForm, \
    ContentUpdateRequestForm
from users.models import InviteCode, Token, EmailPatternWhitelist

UserModel = get_user_model()


class LoginView(Login):
    form_class = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('graph')
    template_name = 'people/login.html'


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class PasswordResetRequestView(FormView):
    form_class = PasswordResetRequestForm
    template_name = 'people/password_reset_request.html'
    success_url = reverse_lazy('password-reset-request')

    @transaction.atomic
    def form_valid(self, form):
        user = form.cleaned_data['person']
        try:
            token = Token.objects.get(user=form.cleaned_data['person'], valid=True, type=Token.Types.PASSWORD_RESET)
        except Token.DoesNotExist:
            token = Token.create_for_user(form.cleaned_data['person'], token_type=Token.Types.PASSWORD_RESET)
            token.save()

        if settings.PRODUCTION:
            user.email_user(
                _('Trihedron Graph - password reset'),
                get_template('people/email/password_reset_mail.html').render({'token': token.token})
            )
        else:
            print('Trihedron Graph - password reset')
            print(get_template('people/email/password_reset_mail.html').render({'token': token.token}))

        messages.success(self.request, _('Reset link has been sent to your email'))
        return super().form_valid(form)


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'people/password_reset.html'
    success_url = reverse_lazy('login')

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        try:
            self.token = Token.objects.select_related('user').get(token=kwargs['token'], valid=True,
                                                                  type=Token.Types.PASSWORD_RESET)
        except Token.DoesNotExist:
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.token.user
        return kwargs

    def form_valid(self, form):
        user: Person = self.token.user
        user.set_password(form.cleaned_data['new_password'])
        user.save()

        self.token.delete()

        messages.success(self.request, _('Your password has been successfully changed.'))

        return super().form_valid(form)


class ChangePasswordView(View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user, valid=True, type=Token.Types.PASSWORD_RESET)
        except Token.DoesNotExist:
            token = Token.create_for_user(request.user, token_type=Token.Types.PASSWORD_RESET)
            token.save()
        return HttpResponseRedirect(reverse('password-reset', kwargs=dict(token=token.token)))


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label=_('New email'))

    def __init__(self, *args, **kwargs):
        self.current_email = kwargs.pop('current_email')
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('new_email') == self.current_email:
            raise ValidationError(_('New email has to be different'))

        return self.cleaned_data


class ChangeEmailView(FormView):
    template_name = 'people/email_change.html'
    form_class = ChangeEmailForm
    success_url = reverse_lazy('email_change')

    def get_initial(self):
        return {
            'new_email': self.request.user.email
        }

    def get_form_kwargs(self):
        kwargs = super(ChangeEmailView, self).get_form_kwargs()
        kwargs['current_email'] = self.request.user.email
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        try:
            token = Token.objects.get(
                user=self.request.user,
                valid=True,
                type=Token.Types.EMAIL_CHANGE,
                extra_data__email=form.cleaned_data['new_email']
            )
        except Token.DoesNotExist:
            token = Token.create_for_user(self.request.user, token_type=Token.Types.EMAIL_CHANGE)
            token.extra_data = {
                'email': form.cleaned_data['new_email']
            }
            token.save()

        if settings.PRODUCTION:
            send_mail(
                _('Trihedron Graph - email change'),
                get_template('people/email/change_email.html').render({'token': token.token}),
                None,
                [form.cleaned_data['new_email']]
            )
        else:
            print('Trihedron Graph - email change')
            print(get_template('people/email/change_email.html').render({'token': token.token}))

        messages.success(self.request, _('Confirmation link has been sent to the specified email'))
        return super().form_valid(form)


class ChangeEmailConfirmView(View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        try:
            token = Token.objects.select_related('user').get(
                token=kwargs['token'],
                valid=True,
                type=Token.Types.EMAIL_CHANGE
            )

            user = token.user

            user.email = token.extra_data['email']
            user.save()

        except Token.DoesNotExist:
            return HttpResponseForbidden()

        messages.success(self.request, _('Your email was successfully changed'))

        return HttpResponseRedirect(reverse('person-content-management'))


class ContentUpdateRequestView(FormView):
    form_class = ContentUpdateRequestForm
    template_name = 'people/content_update.html'
    success_url = reverse_lazy('content_update_submit')

    @transaction.atomic
    def form_valid(self, form):
        update_request = form.save(commit=False)
        update_request.submitted_by = self.request.user
        update_request.save()

        messages.success(self.request, _('Your content has been submitted for review'))

        return super().form_valid(form)


class RegistrationView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'people/registration.html'

    def dispatch(self, request, *args, **kwargs):
        self.invite_code = None
        if 'code' in request.GET:
            try:
                self.invite_code = InviteCode.objects.get(code=request.GET['code'], user__isnull=True)
            except InviteCode.DoesNotExist:
                pass

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['has_invite'] = self.invite_code is not None
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['invite_code'] = self.invite_code
        data['allowed_patterns'] = ', '.join(
            [whitelist.pattern.replace('\\', '').replace('$', '').replace('.*', '') for whitelist in
             EmailPatternWhitelist.objects.all()])
        return data

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        if self.invite_code:
            self.invite_code.user = user
            self.invite_code.save()

        user.is_active = False
        user.save()

        token = Token.create_for_user(user, token_type=Token.Types.ACCOUNT_ACTIVATION)
        token.save()

        if settings.PRODUCTION:
            user.email_user(
                _('Trihedron Graph - registration confirmation'),
                get_template('people/email/activation_email.html').render({'token': token.token})
            )
        else:
            print('Trihedron Graph - registration confirmation')
            print(get_template('people/email/activation_email.html').render({'token': token.token}))

        messages.success(self.request, _('Activation link has been sent to your email'))
        return super().form_valid(form)


class AccountActivationView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(token=kwargs['token'], valid=True, type=Token.Types.ACCOUNT_ACTIVATION)
        except Token.DoesNotExist:
            return HttpResponseRedirect(reverse('registration'))

        token.user.is_active = True
        token.user.save()
        token.delete()
        login(self.request, token.user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, _('Your account has been successfully activated'))
        return HttpResponseRedirect(reverse('person-content-management'))


class LoginOverrideView(FormView):
    template_name = 'people/login_override.html'
    form_class = LoginOverrideForm

    success_url = reverse_lazy('person-content-management')

    def form_valid(self, form):
        login(self.request, form.cleaned_data['login_as'], backend='django.contrib.auth.backends.ModelBackend')

        return super().form_valid(form)
