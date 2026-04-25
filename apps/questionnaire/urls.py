from django.urls import path

from apps.questionnaire import views


app_name = "questionnaire"

urlpatterns = [
    path("<str:deal_id>/", views.questionnaire_start, name="start"),
]