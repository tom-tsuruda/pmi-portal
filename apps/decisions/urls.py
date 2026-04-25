from django.urls import path

from apps.decisions import views


app_name = "decisions"

urlpatterns = [
    path("", views.decision_list, name="list"),
    path("create/", views.decision_create, name="create"),
    path("<str:decision_id>/status/", views.decision_update_status, name="update_status"),
]