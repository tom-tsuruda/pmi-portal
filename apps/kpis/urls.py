from django.urls import path

from apps.kpis import views


app_name = "kpis"

urlpatterns = [
    path("", views.kpi_list, name="list"),
    path("create/", views.kpi_create, name="create"),
]