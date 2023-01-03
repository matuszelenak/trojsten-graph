from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import Relationship
from people.views.graph_v2.common import RelationshipSerializer


class UserRelationshipsView(APIView):
    def get(self, request, *args, **kwargs):
        objs = Relationship.objects.with_people().with_recent_statuses().filter(
            Q(first_person=request.user) | Q(second_person=request.user)
        )
        serializer = RelationshipSerializer(instance=objs, many=True)
        return Response(data=serializer.data)
