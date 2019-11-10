from rest_framework import serializers

from people.models import Person, Relationship, GroupMembership, RelationshipStatus


class GroupMembershipSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name')
    duration = serializers.IntegerField(source='duration.days')

    class Meta:
        model = GroupMembership
        fields = ('date_started', 'date_ended', 'duration', 'group_name')


class PeopleSerializer(serializers.ModelSerializer):
    memberships = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    def get_age(self, instance):
        return instance.age.days / 365

    def get_memberships(self, instance):
        return GroupMembershipSerializer(instance.visible_memberships, many=True).data

    class Meta:
        model = Person
        fields = ('id', 'age', 'first_name', 'last_name', 'maiden_name', 'nickname', 'gender', 'birth_date', 'memberships')


class RelationshipStatusSerializer(serializers.ModelSerializer):
    days_together = serializers.IntegerField(source='duration.days')

    class Meta:
        model = RelationshipStatus
        fields = ('status', 'date_start', 'date_end', 'days_together')


class RelationshipSerializer(serializers.ModelSerializer):
    statuses = serializers.SerializerMethodField()
    source = serializers.IntegerField(source='first_person.pk')
    target = serializers.IntegerField(source='second_person.pk')

    def get_statuses(self, instance):
        return RelationshipStatusSerializer(instance.recent_statuses, many=True).data

    class Meta:
        model = Relationship
        fields = ('source', 'target', 'statuses')
