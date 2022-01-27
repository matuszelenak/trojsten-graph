import datetime
import re
from dataclasses import dataclass
from typing import Union

from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import MultiWidget, Select, CharField
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

VARIABLE_RESOLUTION_DATE_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')
VARIABLE_RESOLUTION_DATE_LENGTH = 10


@dataclass
class VariableDate:
    year: int
    month: int
    day: int


def parse(value) -> Union[VariableDate, datetime.date]:
    match = VARIABLE_RESOLUTION_DATE_RE.match(force_str(value))
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        if month != 0 and day != 0:
            try:
                return datetime.date(year, month, day)
            except ValueError:
                raise ValidationError(f'Must be a valid year, year-month, or year-month-day')

        else:
            if month == 0 and day != 0:
                raise ValidationError(f"Can't specify day without a month")

            return VariableDate(year, month, day)

    raise ValidationError(f'Must be a valid year, year-month, or year-month-day')


class VariableResolutionDateField(models.CharField):
    description = 'A year, year-month, or year-month-day date'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = VARIABLE_RESOLUTION_DATE_LENGTH
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs['max_length'] == VARIABLE_RESOLUTION_DATE_LENGTH:
            del kwargs['max_length']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return parse(value)

    def to_python(self, value):
        if isinstance(value, VariableDate) or isinstance(value, datetime.date):
            return value

        if value is None:
            return value

        return parse(value)

    def get_prep_value(self, value: Union[datetime.date, VariableDate]):
        if value is None:
            return value
        return f'{value.year}-{value.month:02}-{value.day:02}'

    def clean(self, value, model_instance):
        value = self.to_python(value)
        self.validate(value, model_instance)
        return value

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': VariableResolutionDateFormField,
            **kwargs,
        })


class Datalist(Select):
    allow_multiple_selected = False
    input_type = 'text'
    template_name = 'people/forms/datalist.html'
    option_template_name = 'people/forms/datalist_option.html'
    add_id_index = False
    checked_attribute = {'selected': True}
    option_inherits_attrs = False

    def format_value(self, value):
        if value is None:
            return ''

        return str(value)


class DateSelectorWidget(MultiWidget):
    def __init__(self, attrs=None, years=None):
        days = [("", "")] + [(str(x), str(x)) for x in range(1, 32)]
        months = [
            ("", ""),
            ("1", _("January")),
            ("2", _("February")),
            ("3", _("March")),
            ("4", _("April")),
            ("5", _("May")),
            ("6", _("June")),
            ("7", _("July")),
            ("8", _("August")),
            ("9", _("September")),
            ("10", _("October")),
            ("11", _("November")),
            ("12", _("December")),
        ]
        years = [("", "")] + [(str(x), str(x)) for x in range(1900, 2023)]

        _widgets = (
            Select(attrs=attrs, choices=days),
            Select(attrs=attrs, choices=months),
            Datalist(attrs=dict(size=4, **(attrs or {})), choices=years),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if isinstance(value, list):
            return value[:3]

        if isinstance(value, (datetime.date, VariableDate)):
            return [value.day, value.month, value.year]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        date_parts = [widget.value_from_datadict(data, files, name + '_%s' % i) \
                      for i, widget in enumerate(self.widgets)]

        return date_parts


class VariableResolutionDateFormField(CharField):
    widget = DateSelectorWidget

    def clean(self, value):
        if not self.required and all([x == '' for x in value]):
            return None

        return parse(f'{value[2]}-{value[1].zfill(2)}-{value[0].zfill(2)}')


FORMFIELD_FOR_DBFIELD_DEFAULTS.update({
    VariableResolutionDateField: {
        'form_class': VariableResolutionDateFormField,
        'widget': DateSelectorWidget
    },
})