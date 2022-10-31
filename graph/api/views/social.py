from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from social_core.actions import do_auth, do_complete, do_disconnect
from social_django.utils import psa
from social_django.views import _do_login


@api_view(['GET'])
@permission_classes([])
@never_cache
@psa('complete')
def auth(request, backend):
    return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)


@api_view(['GET', 'POST'])
@permission_classes([])
@never_cache
@psa('complete')
def complete(request, backend, *args, **kwargs):
    return do_complete(request.backend, _do_login, user=request.user,
                       redirect_name=REDIRECT_FIELD_NAME, request=request,
                       *args, **kwargs)


@api_view(['GET', 'POST'])
@api_view(['GET'])
@never_cache
@psa()
def disconnect(request, backend, association_id=None):
    return do_disconnect(request.backend, request.user, association_id, redirect_name=REDIRECT_FIELD_NAME)
