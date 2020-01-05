from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as Login
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from people.models import Person, Relationship, ContentSuggestion, Token
from people.serializers import PeopleSerializer, RelationshipSerializer


class LoginView(Login):
    redirect_authenticated_user = True
    success_url = reverse_lazy('graph')
    template_name = 'people/login.html'


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class GraphView(TemplateView):
    template_name = 'people/graph.html'


class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        people = Person.objects.for_graph_serialization()
        response_data = {
            'nodes': PeopleSerializer(people, many=True).data,
            'edges': RelationshipSerializer(Relationship.objects.for_graph_serialization(people), many=True).data
        }
        return JsonResponse(response_data)


class ContentSuggestionSubmitForm(forms.ModelForm):
    class Meta:
        model = ContentSuggestion
        fields = ('suggestion',)
        widgets = {
            'suggestion': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
        }


class ContentSuggestionSubmitView(FormView):
    form_class = ContentSuggestionSubmitForm
    template_name = 'people/suggestion.html'
    success_url = reverse_lazy('suggestion_submit')

    @transaction.atomic
    def form_valid(self, form):
        suggestion = form.save(commit=False)
        suggestion.submitted_by = self.request.user
        suggestion.save()

        messages.success(self.request, 'Your suggestion has been submitted for review')

        return super().form_valid(form)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        if not any([pattern.match(email) for pattern in settings.ALLOWED_MAIL_PATTERNS]):
            self.add_error('email', 'The email pattern is invalid')

        if User.objects.filter(email=email).exists():
            self.add_error('email', 'User with this email already exists')

        if len(self.cleaned_data.get('password', '')) < 8:
            self.add_error('password', 'Password must be at least 8 characters long')
            return self.cleaned_data
        
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Passwords don\'t match')
            
        return self.cleaned_data
    
    class Meta:
        model = User
        fields = ('email', 'username',  'password', 'password_confirm', 'first_name', 'last_name',)
    

class RegistrationView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'people/registration.html'

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()

        token = Token.create_for_user(user)
        token.save()

        user.email_user(
            'Trojsten Graph - registration confirmation',
            get_template('people/activation_email.html').render({'token': token.token, 'request': self.request})
        )

        messages.success(self.request, 'Activation link has been sent to your email')
        return super().form_valid(form)


class AccountActivationView(View):
    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(token=kwargs['token'], valid=True, type=Token.Types.ACCOUNT_ACTIVATION)
        except Token.DoesNotExist:
            return HttpResponseRedirect(reverse('registration'))

        token.user.is_active = True
        token.user.save()
        login(self.request, token.user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(reverse('graph'))
