from django.urls import path

from apps.raid import views


app_name = "raid"

urlpatterns = [
    path("", views.raid_list, name="list"),
    path("create/", views.raid_create, name="create"),
    path("<str:raid_id>/status/", views.raid_update_status, name="update_status"),
]