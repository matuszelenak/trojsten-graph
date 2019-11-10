from django.conf.urls import url

from people.views import token_auth
from . import views


urlpatterns = [
    url(r'^$', token_auth(views.GraphView.as_view()), name='graph'),
    url(r'^graph-data/$', token_auth(views.GraphDataView.as_view()), name='graph_data'),
]
