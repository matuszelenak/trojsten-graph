from functools import wraps

from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView as Login
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship, VerificationToken
from people.serializers import PeopleSerializer, RelationshipSerializer


class TokenAuth:
    def __call__(self, view_func):
        @wraps(view_func)
        def _dispatch_method(request, *args, **kwargs):
            if request.user and request.user.is_staff:
                return view_func(request, *args, **kwargs)

            token = request.GET.get('token')
            if token and VerificationToken.objects.filter(valid_until__gt=timezone.localtime(), token=token).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return _dispatch_method


token_auth = TokenAuth()


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
