from django.conf import settings
from django.urls import re_path, path
from social_core.utils import setting_name

from api.views.graph import graph_view
from api.views.groups import GroupMembershipListView, GroupListView
from api.views.login import login, logout, get_logged_user
from api.views.personal_info import PersonalInfoView
from api.views.relationships import RelationshipView
from api.views.social import auth, complete, disconnect
from api.views.user import change_password, change_email

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

# app_name = 'api'

urlpatterns = [
    re_path(r'^get-authenticated-user/$', get_logged_user, name='get_authenticated_user'),

    re_path(r'^login/$', login, name='api-login'),
    re_path(r'^logout/$', logout, name='api-logout'),

    path(f'login/<str:backend>{extra}', auth, name='begin'),
    path(f'complete/<str:backend>{extra}', complete, name='complete'),
    path(f'disconnect/<str:backend>{extra}', disconnect, name='disconnect'),
    path(f'disconnect/<str:backend>/<int:association_id>{extra}', disconnect,
         name='disconnect_individual'),

    re_path(r'^personal-info/$', PersonalInfoView.as_view(), name='personal_info'),

    re_path(r'^groups/$', GroupListView.as_view(), name='groups'),
    re_path(r'^group-memberships/$', GroupMembershipListView.as_view(), name='group_memberships'),
    re_path(r'^relationships/$', RelationshipView.as_view(), name='relationships'),

    re_path(r'graph/$', graph_view, name='graph_people'),

    re_path(r'account/change-password/$', change_password, name='change_password'),
    re_path(r'account/change-email/$', change_email, name='change_email')
]
