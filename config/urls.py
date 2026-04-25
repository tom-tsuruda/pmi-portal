from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),
    path("deals/", include("apps.deals.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("raid/", include("apps.raid.urls")),
    path("documents/", include("apps.documents.urls")),
    path("questionnaire/", include("apps.questionnaire.urls")),
    path("decisions/", include("apps.decisions.urls")),
    path("approvals/", include("apps.approvals.urls")),
    path("audit/", include("apps.audit.urls")),
]