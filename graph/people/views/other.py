import base64

from django.db import transaction
from django.http import HttpResponse

from people.models import Person
from users.models import Token

PIXEL_GIF_DATA = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


@transaction.atomic
def email_read(request, token):
    try:
        user: Person = Token.objects.select_related('user').get(
            token=token,
            type=Token.Types.AUTH
        ).user
        user.apology_status = Person.ApologyStatus.READ
        user.save()

    except Token.DoesNotExist:
        pass

    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
