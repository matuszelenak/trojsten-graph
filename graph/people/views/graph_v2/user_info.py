from rest_framework.generics import RetrieveUpdateAPIView

from people.views.graph_v2.common import PersonSerializer


class PersonalInfoView(RetrieveUpdateAPIView):
    serializer_class = PersonSerializer

    def get_object(self):
        return self.request.user
