from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import GroupMembership
from people.views.graph_v2.common import GroupMembershipSerializer


class UserGroupsView(APIView):
    def get(self, request, *args, **kwargs):
        memberships = GroupMembership.objects.filter(person=request.user)
        serializer = GroupMembershipSerializer(instance=memberships, many=True)
        return Response(data=serializer.data)
