from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship
from people.serializers import PeopleSerializer, RelationshipSerializer


class GraphView(TemplateView):
    template_name = 'people/graph.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.visible:
            messages.error(request, _('To view the Graph you must set yourself to visible as well.'))
            return HttpResponseRedirect(reverse('person-content-management'))

        return super().dispatch(request, *args, **kwargs)


class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.visible:
            return JsonResponse({'error': 'You must set yourself to visible first'})

        people = Person.qs.for_graph_serialization()
        response_data = {
            'nodes': PeopleSerializer(people, many=True).data,
            'edges': RelationshipSerializer(Relationship.objects.for_graph_serialization(people), many=True).data
        }
        return JsonResponse(response_data)


class AboutView(TemplateView):
    template_name = 'people/about.html'
