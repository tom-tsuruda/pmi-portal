from django.urls import path

from apps.approvals import views


app_name = "approvals"

urlpatterns = [
    path("", views.approval_list, name="list"),
    path("create/", views.approval_create, name="create"),
    path("<str:approval_id>/status/", views.approval_update_status, name="update_status"),
]