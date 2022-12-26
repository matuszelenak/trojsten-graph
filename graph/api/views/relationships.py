from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import ListAPIView

from api.views.base import ModelSerializer
from people.models import Relationship, RelationshipStatus


class RelationshipStatusSerializer(ModelSerializer):
    confirmed_by_me = serializers.SerializerMethodField()
    confirmed_by_other = serializers.SerializerMethodField()

    def get_confirmed_by_me(self, obj):
        with RelationshipStatus.PersonPerspective(obj, self.context.get('perspective_of')) as perspective:
            return perspective.confirmed_by_me

    def get_confirmed_by_other(self, obj):
        with RelationshipStatus.PersonPerspective(obj, self.context.get('perspective_of')) as perspective:
            return perspective.confirmed_by_partner

    class Meta:
        model = RelationshipStatus
        fields = ('id', 'status', 'date_start', 'date_end', 'visible', 'confirmed_by_me', 'confirmed_by_other')


class RelationshipSerializer(ModelSerializer):
    other_person_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(RelationshipSerializer, self).__init__(*args, **kwargs)

        self.fields['statuses'] = RelationshipStatusSerializer(many=True, context={'perspective_of': self.context.get('perspective_of')})

    def get_other_person_name(self, obj):
        if obj.first_person == self.context.get('perspective_of'):
            return obj.second_person.name
        else:
            return obj.first_person.name

    class Meta:
        model = Relationship
        fields = ('id', 'statuses', 'other_person_name')


class RelationshipView(ListAPIView):
    serializer_class = RelationshipSerializer

    def get_serializer_context(self):
        return {'perspective_of': self.request.user}

    def get_queryset(self):
        return Relationship.objects.select_related('first_person', 'second_person').filter(
            Q(first_person=self.request.user) | Q(second_person=self.request.user)
        )
