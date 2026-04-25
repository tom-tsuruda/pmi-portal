from django.urls import path

from apps.deals import views


app_name = "deals"

urlpatterns = [
    path("", views.deal_list, name="list"),
    path("create/", views.deal_create, name="create"),
    path("<str:deal_id>/", views.deal_detail, name="detail"),
]