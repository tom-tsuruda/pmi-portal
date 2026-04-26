from django.urls import path

from apps.tasks import views


app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="list"),
    path("create/", views.task_create, name="create"),
    path("<str:task_id>/edit/", views.task_edit, name="edit"),
    path("<str:task_id>/templates/", views.task_related_templates, name="related_templates"),
    path("<str:task_id>/status/", views.task_update_status, name="update_status"),
]