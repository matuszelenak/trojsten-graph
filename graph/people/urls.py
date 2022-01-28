from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^$', login_required(views.GraphView.as_view()), name='graph'),
    re_path(r'^graph-data/$', login_required(views.GraphDataView.as_view()), name='graph_data'),
    re_path(r'^content-management/person/$', login_required(views.PersonContentManagementView.as_view()), name='person-content-management'),
    re_path(r'^content-management/relationships/$', login_required(views.RelationshipsContentManagementView.as_view()), name='relationships-content-management'),
    re_path(r'^content-management/groups/$', login_required(views.GroupContentManagementView.as_view()), name='groups-content-management'),
    re_path(r'^content-management/delete/$', login_required(views.DeletionManagementView.as_view()), name='deletion-content-management')
    # url(r'^about/$', login_required(views.AboutView.as_view()), name='about')
]
