from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.views.base import ModelSerializer
from people.models import Group, GroupMembership


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'category')


class GroupListView(ListAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.order_by('category', 'name')


class GroupMembershipSerializer(ModelSerializer):
    group_id = serializers.SerializerMethodField()

    def get_group_id(self, obj):
        return str(obj.group.id)

    class Meta:
        model = GroupMembership
        fields = ('id', 'date_started', 'date_ended', 'visible', 'group_id')


class GroupMembershipListView(ListAPIView):
    serializer_class = GroupMembershipSerializer

    def get_queryset(self):
        return GroupMembership.objects.select_related('group').filter(person=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = GroupMembershipSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        return Response()
