from django.urls import path
from . import views

app_name = "deals"

urlpatterns = [
    path("", views.deal_list, name="list"),
    path("<str:deal_id>/", views.deal_detail, name="detail"),
]