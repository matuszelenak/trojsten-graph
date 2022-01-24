from typing import Tuple, List

from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm, BaseModelFormSet
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from people.forms import RelationshipStatusFormset, PersonForm, GroupMembershipFormset
from people.models import Person, Relationship
from people.serializers import PeopleSerializer, RelationshipSerializer


class GraphView(TemplateView):
    template_name = 'people/graph.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseNotFound()
        return super().dispatch(request, *args, **kwargs)


class GraphDataView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseNotFound()

        people = Person.qs.for_graph_serialization()
        response_data = {
            'nodes': PeopleSerializer(people, many=True).data,
            'edges': RelationshipSerializer(Relationship.objects.for_graph_serialization(people), many=True).data
        }
        return JsonResponse(response_data)


class AboutView(TemplateView):
    template_name = 'people/about.html'


class ContentManagementView(TemplateView):
    template_name = 'people/content_management.html'

    def get_forms(self, request) -> Tuple[ModelForm, BaseModelFormSet, List[BaseModelFormSet]]:
        person = request.user
        relationships = Relationship.objects.filter(
            Q(first_person=person) | Q(second_person=person)
        )

        if request.method == 'POST':
            extra_kwargs = dict(data=request.POST)
        else:
            extra_kwargs = {}

        return (
                PersonForm(instance=person, prefix='person', **extra_kwargs),
                GroupMembershipFormset(instance=person, prefix='groups', **extra_kwargs),
                [
                    RelationshipStatusFormset(
                        instance=r,
                        prefix=f"relationship_{r.id}",
                        queryset=r.statuses.with_confirmation_status(person).order_by('date_start', 'date_end'),
                        **extra_kwargs
                    )
                    for r in relationships
                ]
            )


    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        person_form, groups, relationships = self.get_forms(request)
        context['person_form'] = person_form
        context['group_memberships'] = groups
        context['relationships'] = relationships
        return self.render_to_response(context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'delete_all' in request.POST:
            user = request.user
            logout(request)
            user.delete()

            return HttpResponseRedirect(reverse('login'))

        person_form, groups, relationships = self.get_forms(request)

        if person_form.is_valid() and groups.is_valid() and all([x.is_valid() for x in relationships]):
            if person_form.has_changed():
                person_form.save()

            if groups.has_changed():
                groups.save()

            relationship_form: ModelForm
            for relationship_form in relationships:
                for status_form in relationship_form:
                    status_form.instance.confirm_for(request.user)
                    if status_form.has_changed():
                        status_form.instance.remove_confirmation_for_partner_of(request.user)

                    status_form.instance.save()

                if relationship_form.instance.statuses.count() == 0:
                    relationship_form.instance.delete()

            messages.success(request, "Changes were successfully saved")
            return HttpResponseRedirect(reverse('content_management'))
        else:
            messages.error(request, "There were mistakes in the form")

        context = self.get_context_data(**kwargs)
        context['person_form'] = person_form
        context['group_memberships'] = groups
        context['relationships'] = relationships
        return self.render_to_response(context)
