from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from people.forms import RelationshipStatusFormset, PersonForm, GroupMembershipFormset, DeletionForm
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


class PersonContentManagementView(FormView):
    template_name = 'people/content_management/person.html'
    form_class = PersonForm
    success_url = reverse_lazy('person-content-management')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class RelationshipsContentManagementView(TemplateView):
    template_name = 'people/content_management/relationships.html'

    def get_form(self, request):
        person = request.user
        relationships = Relationship.objects.filter(
            Q(first_person=person) | Q(second_person=person)
        )

        if request.method == 'POST':
            extra_kwargs = dict(data=request.POST)
        else:
            extra_kwargs = {}

        return [
            RelationshipStatusFormset(
                instance=r,
                prefix=f"relationship_{r.id}",
                queryset=r.statuses.with_confirmation_status(person).order_by('date_start', 'date_end'),
                **extra_kwargs
            )
            for r in relationships
        ]

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relationships'] = self.get_form(request)
        return self.render_to_response(context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        relationships = self.get_form(request)
        if all([x.is_valid() for x in relationships]):
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
            return HttpResponseRedirect(reverse('relationships-content-management'))
        else:
            messages.error(request, "There were mistakes in the form")

        context = self.get_context_data(**kwargs)
        context['relationships'] = relationships
        return self.render_to_response(context)


class GroupContentManagementView(FormView):
    form_class = GroupMembershipFormset
    success_url = reverse_lazy('groups-content-management')
    template_name = 'people/content_management/groups.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        if form.has_changed():
            form.save()
            messages.success(self.request, "Changes were successfully saved")

        return super().form_valid(form)


class DeletionManagementView(FormView):
    form_class = DeletionForm
    success_url = reverse_lazy('login')
    template_name = 'people/content_management/delete.html'

    def form_valid(self, form):
        user = self.request.user
        logout(self.request)
        user.delete()
        return super().form_valid(form)
