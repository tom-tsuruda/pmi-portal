from django.urls import path

from apps.deals import views


app_name = "deals"

urlpatterns = [
    path("", views.deal_list, name="list"),
    path("create/", views.deal_create, name="create"),
    path("<str:deal_id>/", views.deal_detail, name="detail"),
    path("<str:deal_id>/status/", views.deal_update_status, name="update_status"),
    path("<str:deal_id>/archive/", views.deal_archive, name="archive"),
    path("<str:deal_id>/reactivate/", views.deal_reactivate, name="reactivate"),
    path("<str:deal_id>/report/", views.deal_report, name="report"),
]