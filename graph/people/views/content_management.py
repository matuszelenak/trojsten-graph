from functools import cached_property

from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import OuterRef, Exists, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from people.forms import PersonForm, RelationshipStatusFormset, GroupMembershipFormset, DeletionForm
from people.models import ManagementAuthority, Person, Relationship, RelationshipStatus


class ContentManagementView(FormView):
    success_path = None

    def redirect_to(self, view_name, kwargs=None):
        if self.managed_user != self.request.user:
            extra_query_params =  f"?user_override={self.managed_user.pk}"
        else:
            extra_query_params = ""

        return HttpResponseRedirect(
            reverse(view_name, kwargs=kwargs) + extra_query_params
        )

    def get_managed_people(self):
        return Person.objects.filter(
            Exists(
                ManagementAuthority.objects.filter(manager=self.request.user, subject=OuterRef('pk'))
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        managed_user = self.managed_user
        ctx['authenticated_user'] = self.request.user
        ctx['managed_user'] = managed_user
        ctx['managed_people'] = list(self.get_managed_people())
        ctx['relationships'] = Relationship.objects.filter(
            Q(first_person=managed_user) | Q(second_person=managed_user)
        )
        ctx['preserved_query'] = "" if self.managed_user == self.request.user else f"?user_override={self.managed_user.pk}"
        return ctx

    @cached_property
    def managed_user(self):
        if self.request.GET.get('user_override', 'x').isnumeric():
            try:
                return Person.objects.get(
                    Exists(
                        ManagementAuthority.objects.filter(
                            manager=self.request.user,
                            subject_id=int(self.request.GET['user_override'])
                        )
                    ),
                    pk=int(self.request.GET['user_override'])
                )
            except Person.DoesNotExist:
                return self.request.user

        return self.request.user


class PersonContentManagementView(ContentManagementView):
    template_name = 'people/content_management/person.html'
    form_class = PersonForm
    success_path = 'person-content-management'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.managed_user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        if form.has_changed():
            form.save()
            messages.success(self.request, 'Changes were successfully saved.')
        return self.redirect_to(self.success_path)


class RelationshipContentManagementView(ContentManagementView):
    form_class = RelationshipStatusFormset
    success_path = 'relationship-content-management'
    template_name = 'people/content_management/relationship.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.managed_user
        self.relationship = get_object_or_404(
            Relationship,
            Q(first_person=user) | Q(second_person=user),
            pk=int(kwargs['pk'])
        )
        return super().dispatch(request, *args, **kwargs)

    def get_statuses(self):
        return self.relationship.statuses.with_confirmation_status(self.managed_user).order_by('date_start', 'date_end')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        confirmations = []
        for status in self.get_statuses():
            with RelationshipStatus.PersonPerspective(status, self.managed_user) as perspective:
                confirmations.append((perspective.confirmed_by_me, perspective.confirmed_by_partner))

        kwargs['initial_extra'] = [
            {
                'confirmed_by_me': me,
                'confirmed_by_other_person': other
            }
            for me, other in confirmations
        ]
        kwargs['instance'] = self.relationship
        kwargs['queryset'] = self.get_statuses()
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            for status_form in form:
                with RelationshipStatus.PersonPerspective(status_form.instance, self.managed_user) as perspective:
                    perspective.set_confirmed_for_me(status_form.cleaned_data['confirmed_by_me'])
                    if len(set(status_form.changed_data) - {'confirmed_by_me'}) > 0:
                        perspective.set_confirmed_for_partner(False)

            form.save()
            messages.success(self.request, 'Changes were successfully saved.')
            self.relationship.refresh_from_db()
            if not self.relationship.statuses.exists():
                self.relationship.delete()
                return self.redirect_to('person-content-management')

        return self.redirect_to(self.success_path, dict(pk=self.relationship.pk))


class GroupContentManagementView(ContentManagementView):
    form_class = GroupMembershipFormset
    success_path = 'groups-content-management'
    template_name = 'people/content_management/groups.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.managed_user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        if form.has_changed():
            form.save()
            messages.success(self.request, 'Changes were successfully saved.')

        return self.redirect_to(self.success_path)


class DeletionManagementView(ContentManagementView):
    form_class = DeletionForm
    success_path = 'login'
    template_name = 'people/content_management/delete.html'

    def form_valid(self, form):
        user = self.managed_user
        if self.request.user == user:
            logout(self.request)
        user.delete()
        return self.redirect_to('login')
