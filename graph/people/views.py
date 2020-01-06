from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship
from people.serializers import PeopleSerializer, RelationshipSerializer


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
