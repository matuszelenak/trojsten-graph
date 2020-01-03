from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as Login
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship
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
