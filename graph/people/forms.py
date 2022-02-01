from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, ModelForm, Form, BaseInlineFormSet
from django.forms.fields import CharField, BooleanField, EmailField

from people.models import Relationship, RelationshipStatus, Person, GroupMembership


class PersonForm(ModelForm):
    email = EmailField(disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.email:
            del self.fields['email']

    class Meta:
        model = Person
        fields = ('email', 'first_name', 'last_name', 'nickname', 'maiden_name', 'gender', 'birth_date', 'visible')



class RelationshipStatusForm(ModelForm):
    confirmed_by_me = BooleanField(required=False)
    confirmed_by_other_person = BooleanField(disabled=True, required=False, label='Confirmed by the other person')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = ""

    class Meta:
        model = RelationshipStatus
        fields = ('status', 'date_start', 'date_end', 'visible', 'confirmed_by_me')


class RelationshipStatusModelFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        initial_extra = kwargs.pop('initial_extra') or []
        super().__init__(*args, **kwargs)
        for form, extra in zip(self.forms, initial_extra):
            form.initial.update(extra)


RelationshipStatusFormset = inlineformset_factory(
    Relationship, RelationshipStatus, form=RelationshipStatusForm, extra=0, formset=RelationshipStatusModelFormset
)

class GroupMembershipForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupMembershipForm, self).__init__(*args, **kwargs)
        self.fields['group'].label = ""

    class Meta:
        model = GroupMembership
        fields = ('group', 'date_started', 'date_ended', 'visible')

GroupMembershipFormset = inlineformset_factory(
    Person, GroupMembership, form=GroupMembershipForm, extra=0
)

class DeletionForm(Form):
    confirmation = CharField(label="")

    def clean_confirmation(self):
        c = self.cleaned_data.get('confirmation')
        if c != 'delete':
            raise ValidationError("Incorrect confirmation phrase")
        return c