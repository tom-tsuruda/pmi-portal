from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="deals:list", permanent=False)),
    path("admin/", admin.site.urls),
    path("deals/", include("apps.deals.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("raid/", include("apps.raid.urls")),
    path("documents/", include("apps.documents.urls")),
]