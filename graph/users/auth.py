from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.middleware import AuthenticationMiddleware

from people.models import Person
from users.models import Token

TOKEN_QUERY_PARAM = "auth_token"


class AuthTokenMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        try:
            token = request.GET[TOKEN_QUERY_PARAM]
        except KeyError:
            return

        try:
            auth_token = Token.objects.select_related('user').get(
                type=Token.Types.AUTH,
                token=token,
                valid=True
            )
        except Token.DoesNotExist:
            return

        if request.user.is_authenticated:
            if auth_token.token == token:
                return
            else:
                auth.logout(request)

        user: Person = auth.authenticate(request, token=auth_token)
        if user:
            # user.apology_status = Person.ApologyStatus.READ
            # user.save()

            request.user = user
            auth.login(request, user)


class AuthTokenBackend(ModelBackend):
    def authenticate(self, request, token=None, **kwargs):
        if not token:
            return None

        return token.user
