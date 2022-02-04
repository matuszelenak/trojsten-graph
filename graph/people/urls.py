from django.contrib.auth.decorators import login_required
from django.urls import re_path
from django.views.generic import RedirectView

from .views.content_management import PersonContentManagementView, RelationshipContentManagementView, \
    GroupContentManagementView, DeletionManagementView
from .views.graph import GraphView, GraphDataView

urlpatterns = [
    re_path(r'^$', login_required(GraphView.as_view()), name='graph'),
    re_path(r'^graph-data/$', login_required(GraphDataView.as_view()), name='graph_data'),

    re_path(r'^content-management/$', login_required(RedirectView.as_view(pattern_name='person-content-management', permanent=True))),
    re_path(r'^content-management/person/$', login_required(PersonContentManagementView.as_view()), name='person-content-management'),
    re_path(r'^content-management/relationship/(?P<pk>\d+)/$', login_required(RelationshipContentManagementView.as_view()), name='relationship-content-management'),
    re_path(r'^content-management/groups/$', login_required(GroupContentManagementView.as_view()), name='groups-content-management'),
    re_path(r'^content-management/delete/$', login_required(DeletionManagementView.as_view()), name='deletion-content-management')
    # url(r'^about/$', login_required(views.AboutView.as_view()), name='about')
]
