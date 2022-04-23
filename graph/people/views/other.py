import base64

from django.http import HttpResponse

PIXEL_GIF_DATA = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


def email_read(request, token):
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
