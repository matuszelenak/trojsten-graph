from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import Person
from people.utils.serializers import ModelSerializer
from people.utils.variable_res_date import timedelta
from people.views.graph_v2.common import GroupMembershipSerializer


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


class PeopleView(APIView):
    def get(self, request):
        if not request.user.visible:
            return Response({'error': 'You must set yourself to visible first'})
        people = Person.qs.for_graph_serialization()
        serializer = PeopleSerializer(people, many=True)
        return Response(serializer.data)
