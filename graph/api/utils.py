from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication
from sentry_sdk import capture_exception


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def sentry_capture_exception_handler(exc, context):
    if isinstance(exc, exceptions.APIException) and exc.status_code > 500:
        capture_exception(exc)
    from rest_framework.views import exception_handler
    return exception_handler(exc, context)
