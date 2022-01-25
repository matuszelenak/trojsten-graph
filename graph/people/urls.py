from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^$', login_required(views.GraphView.as_view()), name='graph'),
    re_path(r'^graph-data/$', login_required(views.GraphDataView.as_view()), name='graph_data'),
    re_path(r'^content-management/$', login_required(views.ContentManagementView.as_view()), name='content_management')
    # url(r'^about/$', login_required(views.AboutView.as_view()), name='about')
]
