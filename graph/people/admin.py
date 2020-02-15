from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from people.models import Person, Group, Relationship, RelationshipStatus, PersonNote, RelationshipStatusNote, GroupMembership


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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nickname', 'birth_date')
    search_fields = ('first_name', 'last_name', 'nickname', )
    list_filter = ('visible', 'memberships__group')
    inlines = (PersonNoteInline, GroupMembershipInline)
    exclude = ('notes',)


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
    fields = ('date_start', 'date_end', 'status', 'visible')
    ordering = ['date_start']


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    raw_id_fields = ('first_person', 'second_person')
    search_fields = [f'{person}__{field}' for person in ('first_person', 'second_person') for field in PersonAdmin.search_fields]
    inlines = (RelationshipStatusInline, )

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


site.unregister(User)


@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_superuser', 'date_joined', 'last_login', )
    ordering = ('-date_joined', )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj and obj.user == request.user:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)

        return super().get_queryset(request).filter(user=request.user)
