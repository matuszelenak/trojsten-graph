from django.forms import forms, inlineformset_factory, ModelForm, formset_factory, DateInput

from people.models import Relationship, RelationshipStatus, Person, GroupMembership


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'nickname', 'maiden_name', 'gender', 'birth_date')
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'})
        }

RelationshipStatusFormset = inlineformset_factory(
    Relationship, RelationshipStatus, fields=('status', 'date_start', 'date_end'), extra=0,
    widgets={'date_start': DateInput(attrs={'type': 'date'}), 'date_end': DateInput(attrs={'type': 'date'})}
)

GroupMembershipFormset = inlineformset_factory(
    Person, GroupMembership, fields=('date_started', 'date_ended'), extra=0,
    widgets={'date_started': DateInput(attrs={'type': 'date'}), 'date_ended': DateInput(attrs={'type': 'date'})}

)