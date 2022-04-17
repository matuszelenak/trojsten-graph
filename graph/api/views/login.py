from django.contrib.auth import login as _login, logout as _logout, authenticate
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from people.models import Person


class PersonSerializer(serializers.ModelSerializer):
    session_expires_in = serializers.SerializerMethodField()

    def get_session_expires_in(self, obj):
        return self.context.get('expires_in')

    class Meta:
        model = Person
        fields = ('email', 'session_expires_in')


def get_authenticated_user(request):
    expires_in = (request.session.get_expiry_date() - timezone.now()).seconds
    serializer = PersonSerializer(request.user, context=dict(expires_in=expires_in))

    return Response(serializer.data)


@api_view(['GET'])
def get_logged_user(request):
    return get_authenticated_user(request)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(trim_whitespace=False, write_only=True)
    remember = serializers.BooleanField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


@transaction.atomic
@api_view(['POST'])
@permission_classes([])
def login(request):
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    _login(request, user)

    # Expiry on browser close
    if not serializer.validated_data.get('remember', False):
        request.session.set_expiry(0)

    return get_authenticated_user(request)


@transaction.atomic
@api_view(['POST'])
def logout(request):
    _logout(request)
    return Response()
