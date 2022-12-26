import operator
from functools import reduce

from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.views.base import timedelta, ModelSerializer
from people.models import Person, Relationship, GroupMembership, RelationshipStatus


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
        fields = (
            'id', 'first_name', 'last_name', 'maiden_name', 'nickname', 'gender', 'birth_date', 'death_date', 'age',
            'memberships')


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


@transaction.atomic
@api_view(['GET'])
def graph_view(request):
    if not request.user.visible:
        return Response({'error': 'You must set yourself to visible first'})

    people = Person.qs.for_graph_serialization()
    relationships = Relationship.objects.for_graph_serialization(people)

    return Response(
        data={
            'people': PeopleSerializer(people, many=True).data,
            'relationships': RelationshipSerializer(relationships, many=True).data
        }
    )
