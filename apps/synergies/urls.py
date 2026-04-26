from django.urls import path

from apps.synergies import views


app_name = "synergies"

urlpatterns = [
    path("", views.synergy_list, name="list"),
    path("create/", views.synergy_create, name="create"),
    path("<str:synergy_id>/edit/", views.synergy_edit, name="edit"),
]