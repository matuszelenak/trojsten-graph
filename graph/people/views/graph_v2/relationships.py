from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import Relationship, Person
from people.views.graph_v2.common import RelationshipSerializer


class RelationshipView(APIView):
    def get(self, request):
        if not request.user.visible:
            return Response({'error': 'You must set yourself to visible first'})

        people = Person.qs.for_graph_serialization()
        relationships = Relationship.objects.for_graph_serialization(people)
        serializer = RelationshipSerializer(relationships, many=True)
        return Response(serializer.data)
