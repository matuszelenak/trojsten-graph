from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib import messages
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.forms import formset_factory, BaseFormSet
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.text import gettext_lazy as _
from django.views.generic import FormView

from people.models import ContactEmail, Person


class ContactEmailForm(forms.Form):
    person = forms.ModelChoiceField(queryset=Person.qs.in_age_range(18, None).filter(
        ~Exists(
            ContactEmail.objects.filter(person=OuterRef('pk'), sure_its_active=True)
        ),
        visible=False,
        death_date__isnull=True,
    ).order_by('last_name', 'first_name'), label=_('person'))
    email = forms.EmailField()
    unsure = forms.BooleanField(initial=False, label=_("I'm not sure it's active"), required=False)


class ContactAuthorForm(forms.Form):
    supplier_name = forms.CharField(max_length=256, label=_('Supplier'))
    supplier_email = forms.EmailField(required=False, label=_('Email of the supplier'))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(
        attrs={
            'data-theme': 'dark',
        }
    ), label='')


class EmailGatheringView(FormView):
    template_name = 'people/gather_emails.html'
    success_url = reverse_lazy('email_gather')

    def get_form_class(self):
        return formset_factory(ContactEmailForm, extra=1)

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        if 'author_form' not in kwargs:
            kwargs['author_form'] = self.get_author_form()
        return super().get_context_data(**kwargs)

    def get_author_form(self):
        return ContactAuthorForm(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        author_form = self.get_author_form()
        if form.is_valid() and author_form.is_valid():
            return self.form_valid(form, author_form)
        else:
            return self.invalid(form, author_form)

    @transaction.atomic
    def form_valid(self, form: BaseFormSet, author_form):
        contacts = []

        for person_data in form.cleaned_data:
            try:
                contacts.append(
                    ContactEmail(
                        supplier_email=author_form.cleaned_data['supplier_email'],
                        supplier_name=author_form.cleaned_data['supplier_name'],
                        person=person_data['person'],
                        email=person_data['email'],
                        sure_its_active=not person_data['unsure']
                    )
                )
            except KeyError:
                # SEE NO EVIL
                pass

        if len(contacts) == 0:
            messages.warning(self.request, _('You did not submit anything!'))
            return self.render_to_response(self.get_context_data(form=form, author_form=author_form))

        ContactEmail.objects.bulk_create(contacts, batch_size=100)

        messages.success(self.request, _('Changes were successfully saved.'))
        return HttpResponseRedirect(self.get_success_url())

    def invalid(self, form, author_form):
        messages.error(self.request, _('There were errors in the submitted data.'))
        return self.render_to_response(self.get_context_data(form=form, author_form=author_form))
