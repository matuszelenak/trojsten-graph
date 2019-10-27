from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship


class GraphView(TemplateView):
    template_name = 'people/graph.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['person_cls'] = Person
        return data


class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        people = Person.objects.with_seminar_memberships().with_age().order_by('pk')
        relationships = list(Relationship.objects.with_people().for_people(list(people.values_list('pk', flat=True))).with_latest_status())

        response_data = {
            'nodes': [{
                'id': person.pk,
                'nick': person.nickname,
                'gender': person.gender,
                'age': person.age.days / 365 if person.age else 0,
                'seminar_memberships': [
                    {
                        'group': membership.group.name,
                        'from': str(membership.date_started),
                        'to': str(membership.date_ended),
                        'duration': membership.duration.days + 1
                    }
                    for membership in person.seminar_memberships
                ]
            } for person in people],
            'edges': [
                {
                    'source': rel.first_person.pk,
                    'target': rel.second_person.pk,
                    'status': {
                        'is_active': not rel.latest_status[0].date_end,
                        'days_together': rel.latest_status[0].days_together.days + 1,
                    }
                }
                for rel in relationships if rel.latest_status
            ]
        }

        return JsonResponse(response_data)
