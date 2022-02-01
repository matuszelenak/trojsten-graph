from functools import partial
from itertools import groupby
from operator import attrgetter

from django.forms.models import ModelChoiceIterator, ModelChoiceField


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, group_by, group_labeler):
        self.group_by = group_by
        self.group_labeler = group_labeler
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield "", self.field.empty_label
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.group_by):
            yield self.group_labeler(group), [self.choice(obj) for obj in objs]


class GroupedModelChoiceField(ModelChoiceField):
    def __init__(self, *args, choices_group_by, group_labeler, **kwargs):
        if isinstance(choices_group_by, str):
            choices_group_by = attrgetter(choices_group_by)
        elif not callable(choices_group_by):
            raise TypeError('choices_group_by must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, group_by=choices_group_by, group_labeler=group_labeler)
        super().__init__(*args, **kwargs)
