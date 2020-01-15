from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.utils.cache import get_cache_key
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from people.models import Person, Relationship
from people.serializers import PeopleSerializer, RelationshipSerializer


def invalidate_cache(path):
    request = HttpRequest()
    request.path = path
    key = get_cache_key(request)
    if key in cache:
        cache.delete(key)


class GraphView(TemplateView):
    template_name = 'people/graph.html'


# @cache_page(timeout=100)
class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        people = Person.objects.for_graph_serialization()
        response_data = {
            'nodes': PeopleSerializer(people, many=True).data,
            'edges': RelationshipSerializer(Relationship.objects.for_graph_serialization(people), many=True).data
        }
        return JsonResponse(response_data)
