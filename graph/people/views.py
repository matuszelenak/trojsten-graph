from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as Login
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from people.models import Person, Relationship, ContentSuggestion
from people.serializers import PeopleSerializer, RelationshipSerializer


class LoginView(Login):
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
