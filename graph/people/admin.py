from django.contrib import admin
from django.contrib.admin import TabularInline

from people.models import Person, Group, Relationship, RelationshipStatus


class NoteInline(TabularInline):
    model = Person.notes.through
    extra = 0


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nickname', 'birth_date')
    inlines = (NoteInline,)
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


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    pass
