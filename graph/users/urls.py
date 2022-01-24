from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^logout/$', login_required(views.LogoutView.as_view()), name='logout'),
    re_path(r'^content/$', login_required(views.ContentUpdateRequestView.as_view()), name='content_update_submit'),
    re_path(r'^registration/$', views.RegistrationView.as_view(), name='registration'),
    re_path(r'^activation/(?P<token>\w{50})/$', views.AccountActivationView.as_view(), name='activation')
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^force-login/$', views.LoginOverrideView.as_view(), name='login_override'),
    ]