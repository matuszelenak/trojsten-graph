from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, ModelForm, Form, BaseInlineFormSet
from django.forms.fields import CharField, BooleanField
from django.utils.translation import gettext_lazy as _

from people.models import Relationship, RelationshipStatus, Person, GroupMembership, Group
from people.utils.group_select import GroupedModelChoiceField


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'nickname', 'maiden_name', 'gender', 'birth_date', 'visible')



class RelationshipStatusForm(ModelForm):
    confirmed_by_me = BooleanField(required=False, label=_('Confirmed by me'))
    confirmed_by_other_person = BooleanField(disabled=True, required=False, label=_('Confirmed by the other person'))

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
    group = GroupedModelChoiceField(
        queryset=Group.objects.order_by('category', 'name'),
        choices_group_by='category',
        group_labeler=lambda x: next(iter([label for val, label in Group.Categories.choices if val == x]))
    )

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
            raise ValidationError(_("Incorrect confirmation phrase"))
        return c