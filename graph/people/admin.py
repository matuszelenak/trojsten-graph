from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, re_path

from people.models import Person, Group, Relationship, RelationshipStatus, PersonNote, RelationshipStatusNote, \
    GroupMembership, LegalGuardianship


class BaseNoteInlineForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1})
        }

    def save(self, commit=True):
        self.instance.created_by = self.user
        return super().save(commit)


class BaseNoteInline(admin.TabularInline):
    form = BaseNoteInlineForm
    readonly_fields = ('date_created', 'created_by')
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.user = request.user
        return formset


class PersonNoteInline(BaseNoteInline):
    model = PersonNote


class GroupMembershipInline(admin.TabularInline):
    raw_id_fields = ('person',)
    extra = 0
    model = GroupMembership

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.select_related('person').order_by('-date_started')
        return qs


class PersonAgeFilter(admin.SimpleListFilter):
    template = 'people/admin/age_filter.html'
    title = 'In age range'
    parameter_name = 'age_range'

    def lookups(self, request, model_admin):
        return (None, None),

    @staticmethod
    def get_age(value):
        try:
            return max(int(value), 0)
        except ValueError:
            return None

    def queryset(self, request, queryset):
        if self.value():
            age_from, age_to = [self.get_age(x) for x in self.value().split('_')]
            return queryset.in_age_range(age_from, age_to)
        return queryset


class PersonCurrentStatusFilter(admin.SimpleListFilter):
    title = 'Has current relationship with status'
    parameter_name = 'current_status'

    def lookups(self, request, model_admin):
        return RelationshipStatus.StatusChoices.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.has_relationship_status([self.value()])
        return queryset


class PersonDatingStatusFilter(admin.SimpleListFilter):
    title = 'Current dating status'
    parameter_name = 'dating_status'

    def lookups(self, request, model_admin):
        return (
            ('single', 'Single'),
            ('romantic', 'In a romantic relationship')
        )

    def queryset(self, request, queryset):
        if self.value() == 'single':
            return queryset.single()
        if self.value() == 'romantic':
            return queryset.in_romantic_relationship()
        return queryset


site.login_template = 'people/admin/login.html'

@admin.register(get_user_model())
class PersonAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'nickname', 'birth_date', 'date_joined', 'last_login')
    search_fields = ('first_name', 'last_name', 'nickname', )
    list_filter = (PersonAgeFilter, PersonCurrentStatusFilter, PersonDatingStatusFilter, 'gender', 'visible', 'memberships__group')
    inlines = (GroupMembershipInline, )
    exclude = ('notes',)
    change_list_template = 'people/admin/person_changelist.html'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'parent')
    list_filter = ('category', 'visible')
    search_fields = ('name',)
    inlines = (GroupMembershipInline, )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


class RelationshipStatusInline(admin.TabularInline):
    model = RelationshipStatus
    extra = 0
    fields = ('date_start', 'date_end', 'confirmed_by' ,'status', 'visible')
    ordering = ['date_start']


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    raw_id_fields = ('first_person', 'second_person')
    search_fields = [f'{person}__{field}' for person in ('first_person', 'second_person') for field in PersonAdmin.search_fields]
    inlines = (RelationshipStatusInline, )
    change_form_template = 'people/admin/relationship_change.html'

    @transaction.atomic
    def add_child_view(self, request, pk=None):
        if pk:
            r = Relationship.objects.get(pk=pk)
        else:
            r = None
        if request.method == 'POST':
            form = AddChildForm(request.POST, request.FILES)
            if form.is_valid():
                parent_1, parent_2 = form.cleaned_data['parent_1'], form.cleaned_data['parent_2']
                child = form.cleaned_data['child']
                for parent in (parent_1, parent_2):
                    if not parent:
                        continue

                    parent_child_relationship = Relationship.objects.get_or_create_for_people(parent, child)

                    RelationshipStatus.objects.create(
                        relationship=parent_child_relationship,
                        status=RelationshipStatus.StatusChoices.PARENT_CHILD,
                        date_start=child.birth_date
                    )

                siblings = Person.qs.filter(
                    Exists(
                        Relationship.objects.filter(
                            (Q(first_person=OuterRef('pk')) & (Q(second_person=parent_1) | Q(second_person=parent_2))) |
                            (Q(second_person=OuterRef('pk')) & (Q(first_person=parent_1) | Q(first_person=parent_2))),
                            statuses__status=RelationshipStatus.StatusChoices.PARENT_CHILD
                        )
                    )
                )
                for sibling in siblings:
                    sibling_relationship = Relationship.objects.get_or_create_for_people(sibling, child)
                    RelationshipStatus.objects.create(
                        relationship=sibling_relationship,
                        status=RelationshipStatus.StatusChoices.SIBLING,
                        date_start=max(child.birth_date, sibling.birth_date)
                    )

                messages.success(request, f'Registered {child} as a child of {parent_1} {parent_2 if parent_2 else ""}')
                return HttpResponseRedirect(reverse('admin:people_person_changelist'))
        else:
            if r:
                initial = dict(parent_1=r.first_person, parent_2=r.second_person)
            else:
                initial = {}
            form = AddChildForm(initial=initial)

        context = self.admin_site.each_context(request)
        context['form'] = form
        return TemplateResponse(request, 'people/admin/add_child.html', context)

    def get_urls(self):
        return [
            re_path(r'^add_child/(?P<pk>\d+)/$', self.admin_site.admin_view(self.add_child_view), name='add_child'),
                   re_path(r'^add_child/$', self.admin_site.admin_view(self.add_child_view), name='add_child')
        ] + super().get_urls()

    def get_queryset(self, request):
        return super().get_queryset(request).with_people().with_status_for_date()


class RelationshipStatusNoteInline(BaseNoteInline):
    model = RelationshipStatusNote


class RelationshipStatusCurrentFilter(admin.SimpleListFilter):
    title = 'Current'
    parameter_name = 'current'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(date_end__isnull=True)
        if self.value() == 'no':
            return queryset.filter(date_end__isnull=False)
        return queryset


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ('relationship',)
    search_fields = [f'relationship__{person}__{field}' for person in ('first_person', 'second_person') for field in PersonAdmin.search_fields]
    list_display = ('relationship', 'status', 'date_start', 'date_end', 'visible')
    inlines = (RelationshipStatusNoteInline, )
    list_filter = (RelationshipStatusCurrentFilter, 'status', 'visible')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('relationship__first_person', 'relationship__second_person')



class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_superuser', 'date_joined', 'last_login', )
    ordering = ('-date_joined', )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    list_display = ('user', 'action_time', 'content_type', 'object_repr', 'change_message')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class AddChildForm(forms.Form):
    parent_1 = forms.ModelChoiceField(queryset=Person.qs.order_by('last_name', 'first_name'), required=False)
    parent_2 = forms.ModelChoiceField(queryset=Person.qs.order_by('last_name', 'first_name'), required=False)

    child = forms.ModelChoiceField(queryset=Person.qs.order_by('last_name', 'first_name'))

    def clean(self):
        data = self.cleaned_data
        parent_1: Person
        parent_2: Person
        child: Person
        parent_1, parent_2, child = data.get('parent_1'), data.get('parent_2'), data.get('child')
        if not (parent_1 or parent_2):
            raise ValidationError("Child must have at least one parent")
        if parent_1 == parent_2:
            raise ValidationError("Parents must be different people")

        if child == parent_1 or child == parent_2:
            raise ValidationError('Cannot be your own parent')

        if parent_1 and child.birth_date < parent_1.birth_date or parent_2 and child.birth_date < parent_2.birth_date:
            raise ValidationError('Child cannot be younger than their parent. WTF')

        for parent in (parent_1, parent_2):
            if not parent:
                continue

            if RelationshipStatus.objects.filter(
                Q(relationship__first_person=parent, relationship__second_person=child) |
                Q(relationship__second_person=parent, relationship__first_person=child),
                status=RelationshipStatus.StatusChoices.PARENT_CHILD
            ).exists():
                self.add_error('child', f'{parent_1.name} and {child.name} are already a parent and child')

        return self.cleaned_data

@admin.register(LegalGuardianship)
class LegalGuardianshipAdmin(admin.ModelAdmin):
    raw_id_fields = ('guardian', 'guarded')