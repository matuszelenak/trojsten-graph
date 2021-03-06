from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', login_required(views.LogoutView.as_view()), name='logout'),
    url(r'^content/$', login_required(views.ContentUpdateRequestView.as_view()), name='content_update_submit'),
    url(r'^registration/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^activation/(?P<token>\w{50})/$', views.AccountActivationView.as_view(), name='activation')
]
