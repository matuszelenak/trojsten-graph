import operator
from functools import reduce

from rest_framework import serializers

from people.models import GroupMembership, Person, RelationshipStatus, Relationship
from people.utils.serializers import ModelSerializer
from people.utils.variable_res_date import timedelta


class GroupMembershipSerializer(ModelSerializer):
    group_name = serializers.CharField(source='group.name')
    group_category = serializers.IntegerField(source='group.category')
    duration = serializers.SerializerMethodField()

    def get_duration(self, instance):
        return timedelta(instance.date_ended, instance.date_started)

    class Meta:
        model = GroupMembership
        fields = ('date_started', 'date_ended', 'group_name', 'group_category', 'duration', 'group_id')


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'nickname', 'maiden_name', 'gender', 'visible', 'birth_date')


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
