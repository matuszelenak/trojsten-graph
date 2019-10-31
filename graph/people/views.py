from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import available_attrs
from django.views import View
from django.views.generic import TemplateView

from people.models import Person, Relationship, VerificationToken


class TokenAuth:
    def __call__(self, view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _dispatch_method(request, *args, **kwargs):
            if request.user and request.user.is_staff:
                return view_func(request, *args, **kwargs)

            token = request.GET.get('token')
            if token and VerificationToken.objects.filter(valid_until__gt=timezone.localtime(), token=token).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return _dispatch_method


token_auth = TokenAuth()


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

        # TODO rework into some serializer
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
