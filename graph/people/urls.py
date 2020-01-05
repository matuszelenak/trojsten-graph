from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'^$', login_required(views.GraphView.as_view()), name='graph'),
    url(r'^graph-data/$', login_required(views.GraphDataView.as_view()), name='graph_data'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', login_required(views.LogoutView.as_view()), name='logout'),
    url(r'^suggestion/$', login_required(views.ContentSuggestionSubmitView.as_view()), name='suggestion_submit'),
    url(r'^registration/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^activation/(?P<token>\w{50})/$', views.AccountActivationView.as_view(), name='activation')
]
