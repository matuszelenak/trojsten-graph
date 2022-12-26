import datetime

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from people.utils.variable_res_date import ensure_date, VariableResolutionDateField, \
    VariableResolutionDateSerializerField


def timedelta(later, sooner, raw=False):
    first_day = ensure_date(sooner or datetime.datetime.now().date())
    final_day = ensure_date(later or datetime.datetime.now().date())

    relative_delta = relativedelta(final_day, first_day)
    delta = final_day - first_day

    if raw:
        return relative_delta, delta

    return dict(
        years=relative_delta.years,
        months=relative_delta.months,
        days=relative_delta.days,
        total_days=delta.days,
        is_precise=(sooner is None or isinstance(sooner, datetime.date) or sooner.is_precise) and (
                later is None or isinstance(later, datetime.date) or later.is_precise)
    )


class ModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        VariableResolutionDateField: VariableResolutionDateSerializerField,
        **serializers.ModelSerializer.serializer_field_mapping
    }
