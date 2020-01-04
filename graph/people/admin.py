from django import forms
from django.contrib import admin

from people.models import Person, Group, Relationship, RelationshipStatus, PersonNote, RelationshipStatusNote, GroupMembership, ContentSuggestion


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
    list_filter = ('visible', 'memberships__group__name')
    inlines = (PersonNoteInline, GroupMembershipInline)
    exclude = ('notes',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'parent')
    list_filter = ('category', 'visible')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


class RelationshipStatusInline(admin.TabularInline):
    model = RelationshipStatus
    extra = 0
    fields = ('date_start', 'date_end', 'status', 'visible')
    ordering = ['date_start']


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    search_fields = [f'{person}__{field}' for person in ('first_person', 'second_person') for field in PersonAdmin.search_fields]
    readonly_fields = ('first_person', 'second_person')
    inlines = (RelationshipStatusInline, )

    def get_queryset(self, request):
        return super().get_queryset(request).with_people().with_status_for_date()


class RelationshipStatusNoteInline(BaseNoteInline):
    model = RelationshipStatusNote


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ('relationship',)
    search_fields = [f'relationship__{person}__{field}' for person in ('first_person', 'second_person') for field in PersonAdmin.search_fields]
    list_filter = ('status', 'visible')
    inlines = (RelationshipStatusNoteInline, )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('relationship__first_person', 'relationship__second_person')


@admin.register(ContentSuggestion)
class ContentSuggestionAdmin(admin.ModelAdmin):
    readonly_fields = ('suggestion', 'submitted_by', 'date_created')
