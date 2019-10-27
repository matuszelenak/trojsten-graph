from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.GraphView.as_view(), name='graph'),
    url(r'^data/$', views.GraphDataView.as_view(), name='graph_data')
]
