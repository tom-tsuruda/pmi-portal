from django.urls import path

from apps.backups import views


app_name = "backups"

urlpatterns = [
    path("", views.backup_home, name="home"),
    path("create/", views.backup_create, name="create"),
    path("download/", views.backup_download, name="download"),
]