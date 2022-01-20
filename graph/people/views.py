from typing import Tuple, List

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm, BaseModelFormSet
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404
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

        people = Person.objects.for_graph_serialization()
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
        person = get_object_or_404(Person, account=request.user)
        relationships = Relationship.objects.filter(
            Q(first_person=person) | Q(second_person=person)
        )

        if request.method == 'POST':
            return (
                PersonForm(instance=person, prefix='person', data=request.POST),
                GroupMembershipFormset(instance=person, prefix='groups', data=request.POST),
                [
                    RelationshipStatusFormset(
                        instance=r,
                        prefix=f"relationship_{r.id}",
                        queryset=r.statuses.order_by('date_start', 'date_end'),
                        data=request.POST
                    )
                    for r in relationships
                ]
            )
        else:
            return (
                PersonForm(instance=person, prefix='person'),
                GroupMembershipFormset(instance=person, prefix='groups'),
                [
                    RelationshipStatusFormset(instance=r, prefix=f"relationship_{r.id}",
                                              queryset=r.statuses.order_by('date_start', 'date_end'))
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
            person = get_object_or_404(Person, account=request.user)
            person.delete()


        person_form, groups, relationships = self.get_forms(request)

        if person_form.is_valid() and groups.is_valid() and all([x.is_valid() for x in relationships]):
            if person_form.has_changed():
                person_form.save()

            if groups.has_changed():
                groups.save()

            for r in relationships:
                if r.has_changed():
                    r.save()

            messages.success(request, "Changes were successfully saved")
            return HttpResponseRedirect(reverse('content_management'))
        else:
            messages.error(request, "There were mistakes in the form")

        context = self.get_context_data(**kwargs)
        context['person_form'] = person_form
        context['group_memberships'] = groups
        context['relationships'] = relationships
        return self.render_to_response(context)
