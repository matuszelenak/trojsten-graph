from django.conf.urls import url

from people.views import token_auth
from . import views
urlpatterns = [
    url(r'^$', token_auth(views.GraphView.as_view()), name='graph'),
    url(r'^data/$', token_auth(views.GraphDataView.as_view()), name='graph_data'),
    url(r'^enum-data/$', token_auth(views.GraphEnumView.as_view()), name='enum_data')
]