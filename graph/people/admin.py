from django import forms
from django.contrib import admin

from people.models import Person, Group, Relationship, RelationshipStatus, PersonNote, RelationshipStatusNote


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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nickname', 'birth_date')
    inlines = (PersonNoteInline, )
    exclude = ('notes',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'parent')


class RelationshipStatusInline(admin.TabularInline):
    model = RelationshipStatus
    extra = 0
    fields = ('date_start', 'date_end', 'status')
    ordering = ['date_start']


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    readonly_fields = ('first_person', 'second_person')
    inlines = (RelationshipStatusInline, )


class RelationshipStatusNoteInline(BaseNoteInline):
    model = RelationshipStatusNote


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    inlines = (RelationshipStatusNoteInline, )
