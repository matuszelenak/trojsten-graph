from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from people.models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('category', 'name', 'id')


@api_view(['GET'])
def get_groups(request):
    serializer = GroupSerializer(instance=Group.objects.all(), many=True)
    return Response(data=serializer.data)
