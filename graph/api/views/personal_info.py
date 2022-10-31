from rest_framework.generics import RetrieveUpdateAPIView

from api.views.base import ModelSerializer
from people.models import Person


class PersonalInfoSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'nickname', 'maiden_name', 'visible', 'gender', 'birth_date')


class PersonalInfoView(RetrieveUpdateAPIView):
    serializer_class = PersonalInfoSerializer

    def get_object(self):
        return self.request.user
