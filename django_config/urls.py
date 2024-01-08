# imports to config images uploading
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


def division_error(request):
    20 / 0


urlpatterns = [
    path("sentry-test/", division_error),
    path("admin/", admin.site.urls),
    path("", include("epic_events.urls.collaborator")),
    path("", include("epic_events.urls.department")),
    path("", include("epic_events.urls.company")),
    path("", include("epic_events.urls.customer")),
    path("", include("epic_events.urls.contract")),
    path("", include("epic_events.urls.contract_filter")),
    path("", include("epic_events.urls.event")),
    path("", include("epic_events.urls.location")),
]

# images url configuration
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
