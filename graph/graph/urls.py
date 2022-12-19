from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('social_django.urls')),
    re_path(r'^', include('people.urls')),
    re_path(r'^', include('users.urls')),
    re_path(r'^', include('api.urls')),
    path('hijack/', include('hijack.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
