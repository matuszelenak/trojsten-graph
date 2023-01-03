from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('social_django.urls')),
    re_path(r'^', include('people.urls')),
    re_path(r'^', include('users.urls')),
    path('hijack/', include('hijack.urls')),
) + [
    re_path(r'^', include('api.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
