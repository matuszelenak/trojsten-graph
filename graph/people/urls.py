from django.contrib.auth.decorators import login_required
from django.urls import re_path
from django.views.generic import RedirectView

from .views.content_management import PersonContentManagementView, RelationshipContentManagementView, \
    GroupContentManagementView, DeletionManagementView
from .views.graph_v2.groups import get_groups
from .views.graph_v2.user_groups import UserGroupsView
from .views.graph_v2.user_relationships import UserRelationshipsView
from .views.other import email_read
from .views.graph import GraphView, GraphDataView, GraphViewV2
from .views.graph_v2.user_info import PersonalInfoView
from .views.graph_v2.relationships import RelationshipView
from .views.graph_v2.people import PeopleView
from .views.contact_gathering import EmailGatheringView

urlpatterns = [
    re_path(r'^$', login_required(GraphView.as_view()), name='graph'),
    re_path(r'^graph-data/$', login_required(GraphDataView.as_view()), name='graph_data'),

    re_path(r'^v2/$', login_required(GraphViewV2.as_view()), name='graphV2'),
    re_path(r'people/$', login_required(PeopleView.as_view()), name='graph_people'),
    re_path(r'relationships/$', login_required(RelationshipView.as_view()), name='graph_relationships'),
    re_path(r'groups/$', login_required(get_groups), name='groups'),

    re_path(r'user/info/$', login_required(PersonalInfoView.as_view()), name='user_info'),
    re_path(r'user/group-memberships/$', login_required(UserGroupsView.as_view()), name='user_groups'),
    re_path(r'user/relationships/$', login_required(UserRelationshipsView.as_view()), name='user_relationships'),

    re_path(r'^content-management/$', login_required(RedirectView.as_view(pattern_name='person-content-management', permanent=True))),
    re_path(r'^content-management/person/$', login_required(PersonContentManagementView.as_view()), name='person-content-management'),
    re_path(r'^content-management/relationship/(?P<pk>\d+)/$', login_required(RelationshipContentManagementView.as_view()), name='relationship-content-management'),
    re_path(r'^content-management/groups/$', login_required(GroupContentManagementView.as_view()), name='groups-content-management'),
    re_path(r'^content-management/delete/$', login_required(DeletionManagementView.as_view()), name='deletion-content-management'),
    # url(r'^about/$', login_required(views.AboutView.as_view()), name='about')
    re_path(r'^gather-emails/$', (EmailGatheringView.as_view()), name='email_gather'),
    re_path(r'^email-read/(?P<token>\w{50}).gif$', email_read, name='email_read')
]
