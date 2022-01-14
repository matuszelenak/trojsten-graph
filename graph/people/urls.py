from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'^$', views.GDPRView.as_view(), name='gdpr'),
    url(r'^bravosixgoingdark/$', login_required(views.GraphView.as_view()), name='graph'),
    url(r'^graph-data/$', login_required(views.GraphDataView.as_view()), name='graph_data'),
    # url(r'^about/$', login_required(views.AboutView.as_view()), name='about')
]
