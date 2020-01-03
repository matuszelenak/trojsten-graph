from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'^$', login_required(views.GraphView.as_view()), name='graph'),
    url(r'^graph-data/$', login_required(views.GraphDataView.as_view()), name='graph_data'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
]
