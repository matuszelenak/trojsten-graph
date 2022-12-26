from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from people.models import Person


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=512)
    confirm_new_password = serializers.CharField(max_length=512)

    def validate(self, attrs):
        user: Person = self.context.get('user')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password:
            validate_password(new_password, user)

        if confirm_new_password and new_password != confirm_new_password:
            raise serializers.ValidationError(_('The passwords do not match'))

        return attrs


@api_view(['POST'])
def change_password(request):
    user = request.user

    serializer = ChangePasswordSerializer(data=request.data, context={'user': user})
    serializer.is_valid(raise_exception=True)

    user.set_password(serializer.validated_data['new_password'])
    user.save()

    update_session_auth_hash(request, user)

    return Response()


class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


@api_view(['POST'])
def change_email(request):
    user = request.user

    serializer = ChangeEmailSerializer(data=request.data, context={'user': user})
    serializer.is_valid(raise_exception=True)
