from rest_framework.response import Response
from social_core.backends.google import GoogleOAuth2


class GoogleOAuth2ForRest(GoogleOAuth2):
    def auth_html(self):
        pass

    def start(self):
        return Response(data={'auth_url': self.auth_url()})
