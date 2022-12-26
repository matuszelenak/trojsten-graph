import datetime
import operator
from functools import reduce

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import Person, Relationship, GroupMembership, RelationshipStatus
from people.utils.variable_res_date import VariableResolutionDateField, VariableResolutionDateSerializerField, \
    ensure_date


def timedelta(later, sooner, raw = False):
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
        is_precise=(sooner is None or isinstance(sooner, datetime.date) or sooner.is_precise) and (later is None or isinstance(later, datetime.date) or later.is_precise)
    )


class ModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        VariableResolutionDateField: VariableResolutionDateSerializerField,
        **serializers.ModelSerializer.serializer_field_mapping
    }


class GroupMembershipSerializer(ModelSerializer):
    group_name = serializers.CharField(source='group.name')
    group_category = serializers.IntegerField(source='group.category')
    duration = serializers.SerializerMethodField()

    def get_duration(self, instance):
        return timedelta(instance.date_ended, instance.date_started)

    class Meta:
        model = GroupMembership
        fields = ('date_started', 'date_ended', 'group_name', 'group_category', 'duration')


class PeopleSerializer(ModelSerializer):
    memberships = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    def get_age(self, instance):
        return timedelta(instance.death_date, instance.birth_date)

    def get_memberships(self, instance):
        return GroupMembershipSerializer(instance.visible_memberships, many=True).data

    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name', 'maiden_name', 'nickname', 'gender', 'birth_date', 'death_date', 'age', 'memberships')


class RelationshipStatusSerializer(ModelSerializer):
    duration = serializers.SerializerMethodField()

    def get_duration(self, instance):
        return timedelta(instance.date_end, instance.date_start)

    class Meta:
        model = RelationshipStatus
        fields = ('status', 'date_start', 'date_end', 'duration')


class RelationshipSerializer(serializers.ModelSerializer):
    statuses = serializers.SerializerMethodField()
    source = serializers.IntegerField(source='first_person.pk')
    target = serializers.IntegerField(source='second_person.pk')
    duration = serializers.SerializerMethodField()

    def get_duration(self, instance):
        # TODO do proper interval coverage instead
        deltas = [timedelta(status.date_end, status.date_start, raw=True) for status in instance.recent_statuses]
        total_relative = reduce(operator.add, [d[0] for d in deltas])
        total_delta = reduce(operator.add, [d[1] for d in deltas])

        return dict(
            years=total_relative.years,
            months=total_relative.months,
            days=total_relative.days,
            total_days=total_delta.days,
            is_precise=False
        )

    def get_statuses(self, instance):
        return RelationshipStatusSerializer(instance.recent_statuses, many=True).data

    class Meta:
        model = Relationship
        fields = ('id', 'source', 'target', 'statuses', 'duration')


class GraphViewV2(TemplateView):
    template_name = 'people/graphV2.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.visible:
            messages.error(request, _('To view the Graph you must set yourself to visible as well.'))
            return HttpResponseRedirect(reverse('person-content-management'))
        return super().dispatch(request, *args, **kwargs)


class PeopleView(APIView):
    def get(self, request, format=None):
        if not request.user.visible:
            return Response({'error': 'You must set yourself to visible first'})
        people = Person.qs.for_graph_serialization()
        serializer = PeopleSerializer(people, many=True)
        return Response(serializer.data)


class RelationshipView(APIView):
    def get(self, request, format=None):
        if not request.user.visible:
            return Response({'error': 'You must set yourself to visible first'})

        people = Person.qs.for_graph_serialization()
        relationships = Relationship.objects.for_graph_serialization(people)
        serializer = RelationshipSerializer(relationships, many=True)
        return Response(serializer.data)
