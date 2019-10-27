from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship


class GraphView(TemplateView):
    template_name = 'people/graph.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        people = Person.objects.filter(visible=True)
        relationships = list(Relationship.objects.with_people().for_people(list(people.values_list('pk', flat=True))).with_latest_status())

        data['people'] = people
        data['relationships'] = relationships
        return data


class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        people = Person.objects.order_by('pk')
        relationships = list(Relationship.objects.with_people().for_people(list(people.values_list('pk', flat=True))).with_latest_status())

        response_data = {
            'people': [{
                'name': person.pk,
                'nick': person.nickname
            } for person in people],
            'relationships': [
                {
                    'source': rel.first_person.pk,
                    'target': rel.second_person.pk
                }
                for rel in relationships
            ]
        }

        return JsonResponse(response_data)
