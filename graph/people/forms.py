from django.forms import inlineformset_factory, ModelForm, DateInput

from people.models import Relationship, RelationshipStatus, Person, GroupMembership


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'nickname', 'maiden_name', 'gender', 'birth_date', 'visible')


RelationshipStatusFormset = inlineformset_factory(
    Relationship, RelationshipStatus, fields=('status', 'date_start', 'date_end', 'visible'), extra=0
)

GroupMembershipFormset = inlineformset_factory(
    Person, GroupMembership, fields=('group', 'date_started', 'date_ended'), extra=0
)
