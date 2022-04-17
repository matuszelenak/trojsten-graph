from django.urls import re_path

from api.views.login import login, logout, get_logged_user

urlpatterns = [
    re_path(r'^get-authenticated-user/$', get_logged_user, name='get_authenticated_user'),

    re_path(r'^login/$', login, name='api-login'),
    re_path(r'^logout/$', logout, name='api-logout'),
]
